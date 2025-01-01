import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

base_url = "https://myehalal.halal.gov.my/portal-halal/v1//"
data_key = "ZGlyZWN0b3J5L2luZGV4X2RpcmVjdG9yeTs7Ozs"
negeri_code = "01"
cat = "PE"
sub_cat = "PE"
page_no = "1"
url = base_url + f"index.php?data={data_key}=&negeri={negeri_code}&category={cat}&ty={sub_cat}&page={page_no}"

resp = requests.get(url)
soup = BeautifulSoup(resp.content, "html.parser")

# Get table element
tables = soup.find_all('table')

data_dict = {}

for tr in tables[0].find_all('tr'):
    if tr.find('span',{"class": "company-name"}):
        print(tr.find('span',{"class": "company-name"}).text.strip())
    if tr.find('span',{"class": "company-address"}):
        print(tr.find('span',{"class": "company-address"}).text)
    if tr.find('span',{"class": "company-brand"}):        
        print(tr.find('span',{"class": "company-brand"}).text)


def generate_no_of_pages(soup):
    try:
        # Find the element with the class "corporatedesc"
        coporatedesc_class = soup.find('td', {"class": "corporatedesc"})
        if coporatedesc_class:
            # Check if it contains a <b> tag
            b_tag = coporatedesc_class.find('b')
            if b_tag:
                # Extract the last page number
                last_page_no = int(b_tag.text.split(" ")[-1])
                
                # Generate a list of page numbers from 1 to last_page_no
                page_numbers = list(range(1, last_page_no + 1))
                return page_numbers

        # Return an empty list if the element or last page number is not found
        return [1]
    except Exception as e:
        print(e)
        return [1]
    
all_data = []
for tr in tables[0].find_all('tr'):
    data_dict = {}
    print("*"*50)
    company_name = tr.find('span',{"class": "company-name"})
    company_address = tr.find('span',{"class": "company-address"})
    company_brand = tr.find('span',{"class": "company-brand"})
    if company_name:
        company_name = company_name.text.strip()
        print(company_name)
        data_dict['company_name'] = company_name
    if company_address:
        company_address = company_address.text
        print(company_address)
        data_dict['company_address'] = company_address
    if company_brand:
        company_brand = company_brand.text.strip()
        print(company_brand)
        data_dict['company_brand'] = company_brand
    all_data.append(data_dict)
print(all_data)

