import requests
from bs4 import BeautifulSoup
from datetime import datetime


def next_match():
    dico_month = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'Mai':'05', 'Jun':'06', 
            'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
    dico_team = {'Anderlecht':'Anderlecht','Antwerp':'Antwerp','Beerschot VA':'Beerschot VA','Cercle Brugge':'Cercle Brugge',
        'Charleroi':'Charleroi','Club Brugge':'Club Brugge','Dender':'Dender','KRC Genk':'Genk','Gent':'Gent',
        'Kortrijk':'Kortrijk','KV Mechelen':'Mechelen','OH Leuven':'Oud-Heverlee Leuven','La Louviere':'RAAL La Louviere',
        'Sint-Truiden':'St Truiden','Royale Union SG':'St. Gilloise','Standard Liege':'Standard','Zulte-Waregem':'Waregem','Westerlo':'Westerlo'}
    url = 'https://www.soccerstats.com/results.asp?league=belgium&pmtype=bydate'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find(id='btable')
    all_matches = []
    month_actual = datetime.today().month
    year_actual = datetime.today().year
    for tr in table:
        if tr.has_attr('class') and 'odd' in tr['class'] :
            info_match = [td.text.replace("\xa0","") for td in tr.find_all('td', limit=4)]
            if ":" in info_match[2]:
                day_match, month_match = int(info_match[0].split()[1]), int(dico_month[info_match[0].split()[2]])
                if month_actual <= month_match :
                    year_match = year_actual
                else :
                    year_match = year_actual+1
                date_match = f"{day_match:02}/{month_match:02}/{year_match}"
                all_matches.append([
                    date_match,
                    info_match[2],
                    dico_team[info_match[1]],
                    dico_team[info_match[3]]
                ])
    return all_matches

next_match()