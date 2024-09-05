import requests
import pandas as pd
import os
from copy import deepcopy
import numpy as np

def getEntriesFromLeague(league):
    r = requests.get(f"{os.getenv('BASE_URL')}/leagues-classic/{league}/standings/").json()
    df = pd.DataFrame(r["standings"]["results"])
    return df[["entry", "player_name"]]


def buildLeagueDataFrame(league):
    entries = getEntriesFromLeague(league)
    dataframes = []
    for i in range(len(entries)):
        r = requests.get(f"{os.getenv('BASE_URL')}/entry/{entries.iloc[i].entry}/history").json()
        df = pd.DataFrame(r["current"])
        df["entry"] = entries.iloc[i].entry
        df["player_name"] = entries.iloc[i].player_name
        dataframes.append(df)
    return pd.concat(dataframes, axis=0, ignore_index=True)


def calcPointsOffTop(grp):
    grp["points_off_top"] = grp["total_points"].max() - grp["total_points"]
    return grp


def getTeamPoints(team, gw):
    data = requests.get(f"https://fantasy.premierleague.com/api/entry/{team}/event/{gw}/picks/").json()
    df = pd.DataFrame(data["picks"])
    points = []
    for entry in df.to_dict(orient='records'):
        player = deepcopy(entry)
        player_data = requests.get(f"https://fantasy.premierleague.com/api/element-summary/{entry['element']}/").json()
        player_df = pd.DataFrame(player_data["history"])
        player["points"] = player_df[player_df["round"] == gw].iloc[0].total_points * entry["multiplier"]
        points.append(player)
    return pd.DataFrame(points)


def getPlayerPointsStats(team):
    full_data = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
    gw_df = pd.DataFrame(full_data["events"])
    gws = gw_df[gw_df.finished == True].id.values
    stats = []
    for i in gws:
        gw_stats = {
            "gw": i
        }
        team_df = getTeamPoints(team, i)
        team_df = team_df[team_df.multiplier > 0]
        gw_stats["mean"] = team_df.points.mean()
        gw_stats["std"] = np.sqrt(team_df.points.var())
        gw_stats["entry"] = team
        stats.append(gw_stats)
    return pd.DataFrame(stats)


def main():
    df = buildLeagueDataFrame(os.getenv("LEAGUE_ID"))
    df = df.groupby("event").apply(calcPointsOffTop).reset_index(drop=True)
    df["team_value_mil"] = (df.value - df.bank)/10
    df["value_mil"] = df.value/10
    df["bank_mil"] = df.bank/10
    df.to_csv(f"{os.getenv('STATS_PATH')}/stats.csv")
    
    data = requests.get(f"https://fantasy.premierleague.com/api/leagues-classic/{os.getenv('LEAGUE_ID')}/standings/").json()
    league_df = pd.DataFrame(data["standings"]["results"])
    gw_stats = []
    for entry in league_df.entry:
        gw_stats_df = getPlayerPointsStats(entry)
        gw_stats_df["player_name"] = league_df[league_df.entry == entry].iloc[0].player_name
        gw_stats.append(gw_stats_df)
    gw_stats_concat = pd.concat(gw_stats, axis=0, ignore_index=True)
    gw_stats_concat.to_csv(f"{os.getenv('STATS_PATH')}/gw.csv")
    

if __name__ == "__main__":
    main()