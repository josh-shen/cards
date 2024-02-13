import requests
import itertools
import csv

API_KEY = ''

PROPS = ['player_points', 'player_rebounds', 'player_assists']

def fetch_gameID():
    GAMES_ENDPOINT = f'https://api.the-odds-api.com/v4/sports/basketball_nba/events?apiKey={API_KEY}'
    res = requests.get(GAMES_ENDPOINT)
    games = res.json()

    ids = []
    
    for n in games:
        ids.append(n['id'])
    
    return ids

def fetch_props(prop, ids):
    player_list, full_lines = [], []

    for game_id in ids:
        ODDS_ENDPOINT = f'https://api.the-odds-api.com/v4/sports/basketball_nba/events/{game_id}/odds?apiKey={API_KEY}&bookmakers=draftkings&markets={prop}&oddsFormat=american'
        res = requests.get(ODDS_ENDPOINT)
        odds = res.json()

        if odds['bookmakers']:
            lines = odds['bookmakers'][0]['markets'][0]['outcomes']

        for n in lines: 
            if n['description'] not in player_list:
                player_list.append(n['description'])
                full_lines.append(n)

    return [player_list, full_lines]

ids = fetch_gameID()

# build player lines
full_lines = []
full_lines.append(fetch_props('player_points', ids))
full_lines.append(fetch_props('player_rebounds', ids))
full_lines.append(fetch_props('player_assists', ids))

SEASON = '2023-24'
PTS_ENDPOINT = f'https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Per100Possessions&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={SEASON}&SeasonSegment=&SeasonType=Regular%20Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
ADV_ENDPOiNT = f'https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&MeasureType=Advanced&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Per100Possessions&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={SEASON}&SeasonSegment=&SeasonType=Regular%20Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
REB_ENDPOINT = f'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=PerGame&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType=Rebounding&Season={SEASON}&SeasonSegment=&SeasonType=Regular%20Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
AST_ENDPOINT = f'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=PerGame&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType=Passing&Season={SEASON}&SeasonSegment=&SeasonType=Regular%20Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='

headers = {
    'Dnt': '1',
    'Host': 'stats.nba.com',
    'Origin': 'https://www.stats.nba.com',
    'Referer': 'https://www.stats.nba.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

def fetch_pts():
    pts = requests.get(PTS_ENDPOINT, headers=headers)

    pts_stats = pts.json()
    pts_player_list = pts_stats['resultSets'][0]['rowSet']

    return pts_player_list

def fetch_adv():
    adv = requests.get(ADV_ENDPOiNT, headers=headers)

    adv_stats = adv.json()
    adv_player_list = adv_stats['resultSets'][0]['rowSet']

    return adv_player_list
    
def fetch_rebound():
    reb = requests.get(REB_ENDPOINT, headers=headers)

    reb_stats = reb.json()
    reb_player_list = reb_stats['resultSets'][0]['rowSet']

    return reb_player_list

def fetch_passing():
    passing = requests.get(AST_ENDPOINT, headers=headers)

    passing_stats = passing.json()
    passing_play_list = passing_stats['resultSets'][0]['rowSet']

    return passing_play_list

def filter_players(player_list, n):   
    for i, players in enumerate(player_list):
        if n in players:
            return i
    
    return -1

points = fetch_pts()
adv = fetch_adv()
rebound = fetch_rebound()
passing = fetch_passing()

# build csv row
player_row = {}
for i, n in enumerate(full_lines[0][0]):
    if n not in player_row:
        player_row[n] = {}
    
    player_points = filter_players(points, n)
    player_adv = filter_players(adv, n)
    player_row[n]['points'] = []
    player_row[n]['points'].append(full_lines[0][1][i]['point'])
    player_row[n]['points'].append(player_points)
    player_row[n]['points'].append(player_adv)
       
for i, n in enumerate(full_lines[1][0]):
    if n not in player_row:
        player_row[n] = {}

    player_rebound = filter_players(rebound, n)
    player_row[n]['rebounds'] = []
    player_row[n]['rebounds'].append(full_lines[1][1][i]['point'])
    player_row[n]['rebounds'].append(player_rebound)

for i, n in enumerate(full_lines[2][0]):
    if n not in player_row:
        player_row[n] = {}
    
    player_passing = filter_players(passing, n)
    player_row[n]['assists'] = []
    player_row[n]['assists'].append(full_lines[2][1][i]['point'])
    player_row[n]['assists'].append(player_passing)

rows = []

for (n, v) in player_row.items():
    player = []
    player.append(n)                                   #  0 name
    if 'points' in v:
        player.append(v['points'][0])                  #  1 points projection
        player.append(points[v['points'][1]][30])      #  2 75
        player.append(points[v['points'][2]][12])      #  3 fga
        player.append(points[v['points'][2]][13])      #  4 fg%
        player.append(points[v['points'][2]][15])      #  5 3pa
        player.append(points[v['points'][2]][16])      #  6 3p%
        player.append(points[v['points'][2]][18])      #  7 fta
        player.append(points[v['points'][2]][19])      #  8 ft%
        player.append(adv[v['points'][2]][30])         #  9 usage
    else:
        player.append(-1)
        player.append(-1)
        player.append(-1)
        player.append(-1)
        player.append(-1)
        player.append(-1)
        player.append(-1)
        player.append(-1)
        player.append(-1)

    if 'rebounds' in v:
        player.append(v['rebounds'][0])                # 10 rebounds projection
        player.append(rebound[v['rebounds'][1]][8])    # 11 oreb
        player.append(rebound[v['rebounds'][1]][17])   # 12 dreb
        player.append(rebound[v['rebounds'][1]][30])   # 13 reb chances
        player.append(rebound[v['rebounds'][1]][29])   # 14 contest reb 
    else:
        player.append(-1)
        player.append(-1)
        player.append(-1)
        player.append(-1)
        player.append(-1)
    
    if 'assists' in v:
        player.append(v['assists'][0])                 # 15 assists projection
        player.append(passing[v['assists'][1]][10])    # 16 ast
        player.append(passing[v['assists'][1]][13])    # 17 potential ast
        player.append(passing[v['assists'][1]][8])     # 18 passes made
    else:
        player.append(-1)
        player.append(-1)
        player.append(-1)
        player.append(-1)
    
    rows.append(player)

with open('profiles1.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    field = [
        "Player", 
        "points", 
        "75", 
        "%fga 2pt", 
        "fg%", 
        "%3pa", 
        "3p%", 
        "fta", 
        "ft%", 
        'load', #
        "rebounds", 
        "oreb", 
        "dreb", 
        "reb", 
        "reb chances", 
        "%reb chances converted", 
        "contested reb%", 
        "assists", 
        "ast/game", 
        "potential ast", 
        "passes made"
    ]
    
    writer.writerow(field)
    for r in rows:
        writer.writerow([
            r[0],
            r[1],
            r[2] * 0.75,
            f"{((r[3] - r[5]) * 0.75):.2f} ({((r[3] - r[5]) / r[3]):.2f})", 
            r[4] * 100, 
            f"{(r[5] * 0.75):.2f} ({round(r[5] / r[3], 2):.2f})", 
            r[6] * 100, 
            r[7] * 0.75,
            r[8] * 100,
            r[9],
            r[10],
            r[11],
            r[12],
            r[11] + r[12],
            r[13],
            (r[11] + r[12]) / r[13],
            r[14],
            r[15],
            r[16],
            r[17],
            r[18]
        ])