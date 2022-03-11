import requests
from bs4 import BeautifulSoup
import pandas as pd

class SEASON_STAT_LINE:
    def __init__(self, team_name, season, ortg, drtg, nrtg, sos, pace):
        self.team_name = team_name
        self.season = season
        self.ortg = ortg
        self.drtg = drtg
        self.nrtg = nrtg
        self.sos = sos
        self.pace = pace

    def to_dict(self):
        return {
            'team_name': self.team_name,
            'season': self.season,
            'ortg': self.ortg,
            'drtg': self.drtg,
            'nrtg': self.nrtg,
            'sos': self.sos,
            'pace': self.pace,
        }

def get_drtg_plus(input_row):
    return input_row['drtg'] / season_averages.loc[input_row['season']]['drtg'] * 100

start_year = 1956
end_year = 2021
years = list(range(start_year, end_year))

URL = 'https://www.basketball-reference.com/leagues/NBA_{}.html'

stat_lines = []

#in case this tag changes between seasons on bball ref
offrtg = 'off_rtg'
defrtg = 'def_rtg'
netrtg = 'net_rtg'

for year in years:
    try:
        page = requests.get(URL.format(year))
        content = BeautifulSoup(page.content, 'html.parser')
        teams = content.find(id='div_advanced-team').find('tbody').find_all('tr')
        for team in teams:
            stat_lines.append(SEASON_STAT_LINE(team.find(attrs={"data-stat": "team"}).find('a').string, \
                year, \
                float(team.find(attrs={"data-stat": offrtg}).string), \
                float(team.find(attrs={"data-stat": defrtg}).string), \
                float(team.find(attrs={"data-stat": netrtg}).string), \
                float(team.find(attrs={"data-stat": 'sos'}).string), \
                float(team.find(attrs={"data-stat": 'pace'}).string)))
    except Exception as err:
        print("Failure For " + str(year))
        print(err)

seasons = pd.DataFrame.from_records([stat_line.to_dict() for stat_line in stat_lines])
season_averages = seasons.groupby('season').mean().round(3)

print(seasons.head(10))

#seasons['drtg+'] = (seasons['drtg'] / season_averages.loc[seasons['season']]['drtg']) * 100

seasons['drtg+'] = seasons.apply(get_drtg_plus, axis=1)

print(seasons[['team_name', 'season', 'drtg+']].sort_values(by=['drtg+']).head(20))



