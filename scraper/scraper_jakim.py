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
