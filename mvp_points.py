import requests
from bs4 import BeautifulSoup
import pandas as pd

years = list(range(1956, 2021))
#years = list(range(2010, 2021))
URL = 'https://www.basketball-reference.com/awards/awards_{}.html'

all_vote_getters = {}

def getGamesPlayed(id):
    parameter = id[0] + "/" + id
    seasonURL = 'https://www.basketball-reference.com/players/{}.html'
    page = requests.get(seasonURL.format(parameter))
    content = BeautifulSoup(page.content, 'html.parser')
    games_played = int(content.find(id="per_game").find('tfoot').find(attrs={"data-stat": "g"}).string)
    return games_played

for year in years:
    try:
        page = requests.get(URL.format(year))
        content = BeautifulSoup(page.content, 'html.parser')
        if year > 1967 and year < 1977:
            search_id='nba_mvp'
        else:
            search_id = 'mvp'
        vote_getters = content.find(id=search_id).find_all('tr')
        vote_getters.pop(0)
        vote_getters.pop(0)
        for vote_getter in vote_getters:
            if vote_getter.find(attrs={"data-stat": "player"}).get('csk') in all_vote_getters.keys():
                all_vote_getters[vote_getter.find(attrs={"data-stat": "player"}).get('csk')]['shares'].append(float(vote_getter.find(attrs={"data-stat": "award_share"}).string))
            else:
                all_vote_getters[vote_getter.find(attrs={"data-stat": "player"}).get('csk')] = {
                    "shares":[float(vote_getter.find(attrs={"data-stat": "award_share"}).string)],
                    "id": vote_getter.find(attrs={"data-stat": "player"}).get('data-append-csv')
                }
    except Exception as err:
        print("Failure For " + str(year))
        print(err)

formatted_data = {}

for player in all_vote_getters:
    voted_count = len(all_vote_getters[player]['shares'])
    games_played = getGamesPlayed(all_vote_getters[player]['id'])
    total_point_percentage = sum(all_vote_getters[player]['shares'])
    avg_point_percentage = (total_point_percentage/games_played)*1000
    formatted_data[player] = {
        "voted_count": voted_count,
        "total_point_percentage": total_point_percentage,
        "avg_point_percentage": avg_point_percentage,
        "games_played": games_played
    }

data = pd.DataFrame.from_dict(formatted_data).T

print(data.sort_values('avg_point_percentage', 0, False).head(50))