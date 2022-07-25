from .scraper_interface import ScraperInterface
from helper import categories
import pandas as pd
import requests
from bs4 import BeautifulSoup

STATE_LIST = categories.STATE_LIST
CATEGORY_LIST = categories.CATEGORY_LIST


class ScraperJakim(ScraperInterface):
    def __init__(self) -> None:
        super().__init__()
        self._base_url = "https://www.halal.gov.my/v4"
        self._data_key = "ZGlyZWN0b3J5L2luZGV4X2RpcmVjdG9yeTs7Ozs"

    def get_page_source(
        self, state_code: str, category_code: str, page_num: str
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
        self._page_url = f"/index.php?data={self._data_key}=&negeri={state_code}&category={category_code}&page={page_num}&cari="
        resp = requests.get(self._base_url + self._page_url)
        soup = BeautifulSoup(resp.content, "html.parser")
        return soup

    @staticmethod
    def get_last_page(soup: BeautifulSoup):
        find_a_tags = soup.find("table").find_all("a")
        if len(find_a_tags) > 1:
            try:
                last_page = int(find_a_tags[-1].attrs["href"].split("=")[-1])
            except:
                last_page = int(find_a_tags[-1].text)
        else:
            last_page = 1
        return last_page

    @staticmethod
    def address_to_text(list_address):
        adrress_text = "".join([str(i).replace("<br/>", " ") for i in list_address])
        return adrress_text

    @staticmethod
    def get_company_overview_info(company, state, category):
        company_dict = {}
        name = company.find("span", {"class": "company-name"}).text.strip()
        address_text = ScraperJakim.address_to_text(
            company.find("span", {"class": "company-address"}).contents
        )
        brand_name = (
            company.find("span", {"class": "company-brand"})
            .text.split("JENAMA:")[-1]
            .strip()
        )
        halal_status = company.find("i")
        if halal_status != None:
            status = halal_status.text.split("HALAL :")[-1].strip()
        else:
            status = None
        detailed_company_link = company.find("img").attrs["onclick"].split("'")[1]
        company_dict["company_name"] = name
        company_dict["company_address"] = address_text
        company_dict["company_brand"] = brand_name
        company_dict["company_halal_status"] = status
        company_dict["company_info_url"] = detailed_company_link
        company_dict["state"] = detailed_company_link
        company_dict["category"] = detailed_company_link
        return company_dict

    @staticmethod
    def get_all_company_overview_info(li_tag, state, category):
        all_list = []
        for company in li_tag.find_all("li", {"class": "clearfix search-result-data"}):
            all_list.append(
                ScraperJakim.get_company_overview_info(company, state, category)
            )
        return all_list

    def get_data_from_jakim_website(
        self,
    ):
        all_list_data = []
        for state in STATE_LIST:
            print("*" * 50)
            print("Current State: ", state)
            for category in CATEGORY_LIST:
                print("Current Category: ", category)
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
        df.to_csv("all_data_jakim.csv")
