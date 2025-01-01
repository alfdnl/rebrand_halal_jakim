import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import pandas as pd

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
data = pd.read_csv("all_data_jakim_1.csv")  # Replace with your actual CSV file

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

# Define the function to handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text.strip()  # User's query (e.g., restaurant name)
    
    # Search for the query in your data
    result = data[data['company_name'].str.contains(query, case=False, na=False)]
    
    # Respond to the user
    if not result.empty:
        if len(result) > 10:
            response = "Multiple results found for this restaurant. Please be more specific."
        else:
            response = ""
            for _, row in result.iterrows():
                response += f"Restaurant: {row['company_name']}\n"
    else:
        response = "No information found for this restaurant. Please try another name."
    
    # Send the response
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

if __name__ == '__main__':
    application = ApplicationBuilder().token('7813309902:AAHt3hI18qt7RMZtyC3Wg0krs9E7l1MGWxU').build()
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # application.add_handler(echo_handler)
    
    application.run_polling()

