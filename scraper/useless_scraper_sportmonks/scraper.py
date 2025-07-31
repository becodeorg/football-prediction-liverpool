import requests
import pandas as pd
from datetime import datetime, timedelta
import os

API_TOKEN = "kxBWdTSHN2gLqENdSVNtebYdwpI1FeohESbCaQwypB5oJFGrQvhQzTeaYGeC"
CSV_NAME = "matchs.csv"
TODAY = datetime.today()
DATE_END = TODAY.strftime("%Y-%m-%d")
DATE_START = (TODAY - timedelta(days=100)).strftime("%Y-%m-%d")

def append_to_csv(data_list, filename="matchs.csv"):
    df_new = pd.json_normalize(data_list)
    if os.path.exists(filename):
        df_old = pd.read_csv(filename)
        df_combined = pd.concat([df_old, df_new], ignore_index=True, sort=False)
    else:
        df_combined = df_new
    df_combined.to_csv(filename, index=False)

def flatten_all(d, parent_key='', sep='_'):
    items = []

    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_all(v, new_key, sep=sep).items())

    elif isinstance(d, list):
        for i, v in enumerate(d):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.extend(flatten_all(v, new_key, sep=sep).items())

    else:
        items.append((parent_key, d))

    return dict(items)


end = False
for _ in range(10_000):
    URL = f"https://api.sportmonks.com/v3/football/fixtures/between/{DATE_START}/{DATE_END}?api_token={API_TOKEN}&include=scores;participants;league;season;venue;stage"
    page = 1
    while True:
        response = requests.get(f"{URL}&page={page}").json()
        if "data" in response:
            durty_data = response["data"]
            clean_data = [flatten_all(line) for line in durty_data]
            append_to_csv(clean_data)
        if "pagination" not in response:
            end = True
            break
        if response["pagination"]['has_more'] is False :
            break
        print(page, type(response["pagination"]['has_more']))
        page += 1
    if end == True:
        break
    DATE_END = DATE_START
    DATE_START = (datetime.strptime(DATE_START, "%Y-%m-%d") - timedelta(days=100)).strftime("%Y-%m-%d")

print("GOOD")
