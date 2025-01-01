from .scraper_interface import ScraperInterface
from helper import categories
from helper.utils import timer
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

STATE_LIST = categories.STATE_LIST
CATEGORY_LIST = categories.CATEGORY_LIST
SUB_CATEGORY_LIST = categories.SUB_CATEGORY_LIST
STATE_DICT = categories.STATE_DICT


class ScraperJakim(ScraperInterface):
    def __init__(self) -> None:
        super().__init__()
        self._base_url = "https://myehalal.halal.gov.my/portal-halal/v1/"
        self._data_key = "ZGlyZWN0b3J5L2luZGV4X2RpcmVjdG9yeTs7Ozs"

    def get_page_source(
        self,
        state_code: str,
        category_code: str,
        page_num: str,
        subcategory: str = None,
    ) -> BeautifulSoup:
        """
        get_page_source _summary_

        Parameters
        ----------
        state_code : str
            _description_
        category_code : str
            _description_
        page_num : str
            _description_

        Returns
        -------
        BeautifulSoup
            _description_
        """
        if subcategory is None:
            self._page_url = f"/index.php?data={self._data_key}=&negeri={state_code}&category={category_code}&page={page_num}&cari="
        else:
            self._page_url = f"/index.php?data={self._data_key}=&negeri={state_code}&category={category_code}&page={page_num}&ty={subcategory}"
        resp = requests.get(self._base_url + self._page_url)
        soup = BeautifulSoup(resp.content, "html.parser")
        return soup

    @staticmethod
    def get_last_page(soup: BeautifulSoup):
        coporatedesc_class = soup.find("td", {"class": "corporatedesc"})
        if coporatedesc_class:
            # Check if it contains a <b> tag
            b_tag = coporatedesc_class.find_all("b")[-1]
            if b_tag:
                # Extract the last page number
                last_page_no = int(b_tag.text.split(" ")[-1])
                return last_page_no
        return 1

    @staticmethod
    def address_to_text(list_address):
        adrress_text = "".join([str(i).replace("<br/>", " ") for i in list_address])
        return adrress_text

    @staticmethod
    def get_company_overview_info(company, state, category, subcategory=None):
        company_dict = {}
        name = company.find("span", {"class": "company-name"}).text.strip()
        address_text = ScraperJakim.address_to_text(
            company.find("span", {"class": "company-address"}).contents
        )
        brand_name_div = company.find("span", {"class": "company-brand"})

        try:
            detailed_page = (
                company.attrs.get("onclick").split("openModal('")[-1].split("',")[0]
            )
        except Exception as e:
            print("Failed to get detailed page")
            detailed_page = None

        city = ""
        if "W.P." in STATE_DICT[state]:
            city = STATE_DICT[state]
        else:
            for city in categories.STATE_CITY_MAPPING.get(STATE_DICT[state]):
                if city.lower() in address_text.lower():
                    print("Found city: ", city)
                    city = city
                    break
                city = ""
        expiry_date = company.find_all("td")[-1].text.strip()
        company_dict["company_name"] = name
        company_dict["company_brand"] = None
        company_dict["company_halal_status"] = "Halal"
        company_dict["company_address"] = address_text
        company_dict["city"] = city
        company_dict["state"] = STATE_DICT[state]
        company_dict["halal_expiry_date"] = expiry_date
        company_dict["company_info_url"] = detailed_page
        company_dict["category"] = category
        company_dict["subcategory"] = subcategory
        company_dict["scraped_at"] = datetime.now()

        if brand_name_div:
            children = brand_name_div.find_all(recursive=False)
            if len(children) > 2:
                ## Possible changes in halal status
                # get index of halal status
                company_brand = brand_name_div.text.strip()
                index_halal = company_brand.find("STATUS HALAL")
                halal_status = company_brand[index_halal:].split(":")[-1].strip()
                brand_name = company_brand[:index_halal].split(":")[-1].strip()
                company_dict["company_halal_status"] = halal_status
                company_dict["company_brand"] = brand_name
            else:
                company_brand = brand_name_div.text.strip()
                company_dict["company_brand"] = company_brand.split(":")[-1]
        return company_dict

    @staticmethod
    def get_all_company_overview_info(li_tag, state, category, subcategory=None):
        all_list = []
        tables = li_tag.find_all("table")
        table_data = tables[0].find_all("tr", {"class": "border-b"})
        print("Data length: ", len(table_data))
        for company in table_data:
            all_list.append(
                ScraperJakim.get_company_overview_info(
                    company, state, category, subcategory
                )
            )
        return all_list

    @timer
    def get_data_from_jakim_website(
        self,
    ):
        all_list_data = []
        for state in STATE_LIST:
            print("*" * 50)
            print("Current State: ", state)
            for category in CATEGORY_LIST:
                print("Current Category: ", category)
                if category == "PE":
                    print("Scrape SubCategory")
                    for subcategory in SUB_CATEGORY_LIST:
                        page_num = 1
                        soup = self.get_page_source(
                            category_code=category,
                            state_code=state,
                            page_num=page_num,
                            subcategory=subcategory,
                        )
                        print(
                            f"Done Scrapping: \ncurrent url: {self._base_url + self._page_url}"
                        )
                        last_page = self.get_last_page(soup)
                        print(f"Last Page: {last_page}")
                        if last_page == 1:
                            all_list_data.extend(
                                self.get_all_company_overview_info(
                                    soup, state, category, subcategory
                                )
                            )
                        else:
                            for page_num in range(1, last_page + 1):
                                print(f"Currently craping:\nPage: {page_num}")
                                if page_num == 1:
                                    all_list_data.extend(
                                        self.get_all_company_overview_info(
                                            soup, state, category, subcategory
                                        )
                                    )
                                else:
                                    new_soup = self.get_page_source(
                                        category_code=category,
                                        state_code=state,
                                        page_num=page_num,
                                        subcategory=subcategory,
                                    )
                                    all_list_data.extend(
                                        self.get_all_company_overview_info(
                                            new_soup, state, category, subcategory
                                        )
                                    )
                                print(
                                    f"Done Scrapping: \ncurrent url: {self._base_url + self._page_url}"
                                )

                else:
                    page_num = 1
                    soup = self.get_page_source(
                        category_code=category, state_code=state, page_num=page_num
                    )
                    print(
                        f"Done Scrapping: \ncurrent url: {self._base_url + self._page_url}"
                    )
                    last_page = self.get_last_page(soup)
                    if last_page == 1:
                        all_list_data.extend(
                            self.get_all_company_overview_info(soup, state, category)
                        )
                    else:
                        for page_num in range(2, last_page + 1):
                            print(f"Currently craping:\nPage: {page_num}")
                            if page_num == 1:
                                all_list_data.extend(
                                    self.get_all_company_overview_info(
                                        soup, state, category
                                    )
                                )
                            else:
                                new_soup = self.get_page_source(
                                    category_code=category,
                                    state_code=state,
                                    page_num=page_num,
                                )
                                all_list_data.extend(
                                    self.get_all_company_overview_info(
                                        new_soup, state, category
                                    )
                                )
                            print(
                                f"Done Scrapping: \ncurrent url: {self._base_url + self._page_url}"
                            )
                print("*" * 50)
        df = pd.DataFrame(all_list_data)
        df.to_csv("all_data_jakim_1.csv")
