#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example.
"""
import logging
import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import re
from datetime import datetime


def escape_markdown_v2(text):
    """Escapes special characters for Telegram MarkdownV2."""
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", text)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Mock data for states and restaurants
restaurant_data = pd.read_csv("final_all_data.csv")


# Step 1: Start the bot and select state
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message and state selection."""
    states = restaurant_data["state"].unique()
    state_buttons = [
        [InlineKeyboardButton(state, callback_data=state)] for state in states
    ]
    reply_markup = InlineKeyboardMarkup(state_buttons)

    await update.message.reply_text(
        "Sila pilih satu negeri:", reply_markup=reply_markup
    )


# Step 2: Handle state selection
async def state_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles state selection and prompts for restaurant name."""
    query = update.callback_query
    await query.answer()

    selected_state = query.data
    context.user_data["selected_state"] = selected_state

    await query.edit_message_text(
        f"🏠 Anda telah memilih negeri: {selected_state}. Sila masukkan nama restoran."
    )


# Step 3: Handle restaurant search
async def search_restaurant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles restaurant search and city selection if needed."""
    user_input = update.message.text.strip()
    selected_state = context.user_data.get("selected_state")
    query = update.callback_query

    if not selected_state:
        await update.message.reply_text(
            "Sila pilih satu negeri terlebih dahulu menggunakan /start."
        )
        return

    # Filter data by state and restaurant name
    filtered_data = restaurant_data[
        (restaurant_data["state"] == selected_state)
        & (
            restaurant_data["restaurant_name"].str.contains(
                user_input, case=False, na=False
            )
        )
    ]

    if filtered_data.empty:
        await update.message.reply_text(
            f"Tiada hasil yang ditemui untuk '{user_input}' di {selected_state}."
        )
        return

    # If more than 10 results, prompt for city selection
    if len(filtered_data) > 10:
        unique_cities = filtered_data["city"].unique()
        city_buttons = [
            [InlineKeyboardButton(city, callback_data=f"city_{city}")]
            for city in unique_cities
        ]
        logging.info(city_buttons)
        reply_markup = InlineKeyboardMarkup(city_buttons)

        # Save filtered results for later use
        context.user_data["filtered_restaurants"] = filtered_data
        await update.message.reply_text(
            f"Terdapat lebih dari 10 restoran untuk '{user_input}' di {selected_state}.\n\n"
            f"Sila pilih satu bandar yang berdekatan:",
            reply_markup=reply_markup,
        )
    else:
        # Display all results if <=10
        company_buttons = [
            [
                InlineKeyboardButton(
                    text=f"{row['restaurant_name']}",
                    callback_data=f"company_{row['restaurant_name']}",
                )
            ]
            for idx, row in filtered_data.iterrows()
        ]
        reply_markup = InlineKeyboardMarkup(company_buttons)

        # Save city-specific data for further selection
        context.user_data["company_selection_data"] = filtered_data
        await update.message.reply_text(
            f"Sila pilih satu restoran yang anda cari:",
            reply_markup=reply_markup,
        )


# Step 4: Handle city selection
async def city_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles city selection and displays filtered results."""
    query = update.callback_query

    await query.answer()
    logging.info(f"City selected {query.data}")

    selected_city = query.data.replace("city_", "")  # Strip the prefix
    filtered_data = context.user_data.get("filtered_restaurants", pd.DataFrame())

    # Further filter data by city
    city_filtered_data = filtered_data[filtered_data["city"] == selected_city]

    if len(city_filtered_data) > 0:
        company_buttons = [
            [
                InlineKeyboardButton(
                    text=f"{row['restaurant_name']}",
                    callback_data=f"company_{row['restaurant_name']}",
                )
            ]
            for idx, row in city_filtered_data.iterrows()
        ]
        reply_markup = InlineKeyboardMarkup(company_buttons)

        # Save city-specific data for further selection
        context.user_data["company_selection_data"] = city_filtered_data
        await query.edit_message_text(
            f"Terdapat lebih dari 1 restoran di {selected_city}.\n\n"
            f"Sila pilih satu restoran yang berdekatan:",
            reply_markup=reply_markup,
        )
    else:
        # Display the results directly if <=10
        response = f"Tiada restoran halal yang dijumpai di {selected_city}."
        await query.edit_message_text(response)


async def company_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles company selection and sends the selected restaurant details."""
    query = update.callback_query
    await query.answer()

    selected_option = query.data
    selected_restaurant = selected_option.replace("company_", "")
    city_filtered_data = context.user_data.get("company_selection_data", pd.DataFrame())
    company_data = city_filtered_data[
        (city_filtered_data["restaurant_name"] == selected_restaurant)
    ]
    # Get the selected restaurant details
    if not company_data.empty:
        selected_row = company_data.iloc[0]
        # Handle last updated and default for NaN
        last_updated_raw = selected_row.get("scraped_at", None)
        if last_updated_raw:
            # Parse and format the datetime
            last_updated_dt = datetime.strptime(
                last_updated_raw, "%Y-%m-%d %H:%M:%S.%f"
            )
            last_updated_formatted = last_updated_dt.strftime("%d %B %Y, %I:%M %p")
        else:
            last_updated_formatted = "Tidak Diketahui"
        response = (
            f"🍗 *Halal Status Details* 🍗\n\n"
            f"🏠 *Nama Restoran*: {escape_markdown_v2(selected_row['restaurant_name'])}\n"
            f"📍 *Alamat*:\n"
            f"{escape_markdown_v2(selected_row['company_address'])}\n\n"
            f"🏢 *Jenama*: {escape_markdown_v2(selected_row['company_brand']) if not pd.isna(selected_row['company_brand']) else 'Tiada Jenama'}\n\n"
            f"✅ *Status Halal*: {escape_markdown_v2(selected_row['company_halal_status'])}\n\n"
            f"⏰ *Tarikh Data Diperolehi*: {last_updated_formatted}\n\n"
            f"📌 *Nota*: Untuk memastikan maklumat terkini, sila rujuk laman rasmi JAKIM\.\n\n"
            f"🔄 [Klik di sini] /start untuk membuat pencarian semula\."
        )

    else:
        response = "Pilihan tidak sah. Sila cuba lagi. /start untuk mencari semula."

    await query.edit_message_text(response, parse_mode="MarkdownV2")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Klik /start untuk membuat pencarian.")


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token("7813309902:AAHt3hI18qt7RMZtyC3Wg0krs9E7l1MGWxU")
        .build()
    )

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        CallbackQueryHandler(
            state_selected,
            pattern="^(Johor|Selangor|Melaka|Kedah|Kelantan|Perak|Perlis|Pahang|Pulau Pinang|Sabah|Sarawak|W.P. Kuala Lumpur|W.P. Labuan|W.P. Putrajaya)$",
        )
    )
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, search_restaurant)
    )
    application.add_handler(CallbackQueryHandler(city_selected, pattern="^city_.*$"))
    application.add_handler(
        CallbackQueryHandler(company_selected, pattern="^company_.*$")
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
