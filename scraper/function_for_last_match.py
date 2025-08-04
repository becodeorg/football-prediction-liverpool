import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_last_match(h_team, a_team, number_of_match=5):
    url_base = "https://www.football-data.co.uk/"
    response = requests.get(url_base+"belgiumm.php")
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    five_last_match_h_team = pd.DataFrame()
    five_last_match_a_team = pd.DataFrame()
    for link in links:
        link_href = link['href']
        if ".csv" in link_href :
            url_csv = url_base + link_href
            df_year = pd.read_csv(url_csv, index_col=False, skip_blank_lines=True, on_bad_lines='skip')
            df_year = df_year.loc[:, df_year.columns.notna() & ~df_year.columns.str.startswith('Unnamed')]
            df_year_h_team = df_year[(df_year["HomeTeam"] == h_team) | (df_year["AwayTeam"] == h_team)]
            five_last_match_h_team = pd.concat([five_last_match_h_team, df_year_h_team])
            df_year_a_team = df_year[(df_year["HomeTeam"] == a_team) | (df_year["AwayTeam"] == a_team)]
            five_last_match_a_team = pd.concat([five_last_match_a_team, df_year_a_team])
        if len(five_last_match_a_team) >= number_of_match and len(five_last_match_h_team) >= number_of_match:
            five_last_match_a_team['Date'] = pd.to_datetime(five_last_match_a_team['Date'], format='%d/%m/%Y')
            five_last_match_a_team = five_last_match_a_team.sort_values(by='Date', ascending=False)
            five_last_match_h_team['Date'] = pd.to_datetime(five_last_match_h_team['Date'], format='%d/%m/%Y')
            five_last_match_h_team = five_last_match_h_team.sort_values(by='Date', ascending=False)
            return five_last_match_h_team[:number_of_match], five_last_match_a_team[:number_of_match]

print(get_last_match("Antwerp", "Genk"))