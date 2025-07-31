import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

URL = "https://www.football.co.uk/match-reports/"
CSV_FILE = "played_matches.csv"

def fetch_played_matches():
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    rows = []
    current_date = None

    for tr in soup.select("table.table tr"):
        # Si c'est une ligne de date
        if 'row-header' in tr.get("class", []):
            h3 = tr.find("h3")
            if h3:
                current_date = h3.text.strip()
        # Si c'est une ligne de match
        elif tr.find("td", class_="hometeam"):
            tds = tr.find_all("td")
            if len(tds) < 4:
                continue  # ligne incomplète

            home_team = tds[0].text.strip()
            score = tds[1].text.strip()
            away_team = tds[2].text.strip()
            stats_link = tds[3].find("a")["href"]
            full_stats_url = "https://www.football.co.uk" + stats_link

            uid = f"{current_date}|{home_team}|{away_team}"
            rows.append({
                "date": current_date,
                "home_team": home_team,
                "away_team": away_team,
                "score": score,
                "stats_url": full_stats_url,
                "uid": uid
            })

    return pd.DataFrame(rows)

def save_to_csv(df_new):
    if os.path.exists(CSV_FILE):
        df_old = pd.read_csv(CSV_FILE)
        df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset="uid")
    else:
        df_combined = df_new
    df_combined.to_csv(CSV_FILE, index=False)

def main():
    df = fetch_played_matches()
    print(f"DONE")
    save_to_csv(df)

if __name__ == "__main__":
    main()
