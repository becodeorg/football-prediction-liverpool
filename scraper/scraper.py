import requests
from bs4 import BeautifulSoup
import os
import pandas as pd

url_base = "https://www.football-data.co.uk/"

link_df = []

countries = ["belgiumm.php", "englandm.php", "scotlandm.php", "germanym.php", "italym.php", "spainm.php", \
             "francem.php", "netherlandsm.php", "portugalm.php", "turkeym.php", "greecem.php"]

for country in countries :
    url_country = url_base + country
    response = requests.get(url_country)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    for link in links:
        link_href = link['href']
        if '.csv' in link_href:
            url_csv = url_base + link_href
            small_df = pd.read_csv(url_csv, index_col=False, skip_blank_lines=True, on_bad_lines='skip', encoding="ISO-8859-1")
            small_df = small_df.loc[:, small_df.columns.notna() & ~small_df.columns.str.startswith('Unnamed')]
            link_df.append(small_df)

df = pd.concat(link_df, ignore_index=True)
df.to_csv("data.csv", index=False)