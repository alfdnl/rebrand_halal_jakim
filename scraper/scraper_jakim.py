from scraper_interface import ScraperInterface
import requests
from bs4 import BeautifulSoup


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
        last_page = int(
            soup.find("table").find_all("a")[-1].attrs["href"].split("=")[-1]
        )
        return last_page

    @staticmethod
    def address_to_text(list_address):
        adrress_text = "".join([str(i).replace("<br/>", " ") for i in list_address])
        return adrress_text

    @staticmethod
    def get_company_overview_info(company):
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
        return company_dict

    @staticmethod
    def get_all_company_overview_info(li_tag):
        all_list = []
        for company in li_tag.find_all("li", {"class": "clearfix search-result-data"}):
            all_list.append(ScraperJakim.get_company_overview_info(company))
        return all_list
