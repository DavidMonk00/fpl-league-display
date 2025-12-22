import requests
import pandas as pd
import os
from copy import deepcopy
import numpy as np
import logging
import json

from static import BootstrapStatic
from league import League


def calcPointsOffTop(grp):
    grp["points_off_top"] = grp["total_points"].max() - grp["total_points"]
    return grp


def getTeamPoints(players: dict, team, gw):
    data = requests.get(f"https://fantasy.premierleague.com/api/entry/{team}/event/{gw}/picks/").json()
    df = pd.DataFrame(data["picks"])
    points = []
    for entry in df.to_dict(orient='records'):
        logging.debug(entry)
        player = deepcopy(entry)
        if entry['element'] in players:
            player_data = players[entry['element']]
        else:
            player_data = requests.get(f"https://fantasy.premierleague.com/api/element-summary/{entry['element']}/").json()
            players[entry['element']] = player_data
        player_df = pd.DataFrame(player_data["history"])
        try:
            player["points"] = player_df[player_df["round"] == gw].iloc[0].total_points * entry["multiplier"]
        except IndexError:
            player["points"] = 0
        points.append(player)
    return pd.DataFrame(points)


def getPlayerPointsStats(bootstrap_static: BootstrapStatic, players: dict, team):
    gw_df = pd.DataFrame(bootstrap_static.data["events"])
    gws = gw_df[gw_df.finished == True].id.values
    stats = []
    for i in gws:
        gw_stats = {
            "gw": i
        }
        team_df = getTeamPoints(players, team, i)
        team_df = team_df[team_df.multiplier > 0]
        gw_stats["mean"] = team_df.points.mean()
        gw_stats["std"] = np.sqrt(team_df.points.var())
        gw_stats["entry"] = team
        stats.append(gw_stats)
    return pd.DataFrame(stats)


def main():
    bootstrap_static = BootstrapStatic(network=True)
    league = League(os.getenv("LEAGUE_ID"), bootstrap_static)
    df = league.getDataFrame()
    df = df.groupby("event")[df.columns].apply(calcPointsOffTop).reset_index(drop=True)
    df["team_value_mil"] = (df.value - df.bank)/10
    df["value_mil"] = df.value/10
    df["bank_mil"] = df.bank/10
    df.to_csv(f"{os.getenv('STATS_PATH')}/stats.csv")
    logging.info("League stats written to %s/stats.csv", os.getenv('STATS_PATH'))

    data = requests.get(f"{os.getenv('BASE_URL')}/leagues-classic/{os.getenv('LEAGUE_ID')}/standings/", timeout=5).json()
    league_df = pd.DataFrame(data["standings"]["results"])
    gw_stats = []
    players = {}
    for entry in league_df.entry:
        gw_stats_df = getPlayerPointsStats(bootstrap_static, players, entry)
        gw_stats_df["player_name"] = league_df[league_df.entry == entry].iloc[0].player_name
        gw_stats.append(gw_stats_df)
    gw_stats_concat = pd.concat(gw_stats, axis=0, ignore_index=True)
    gw_stats_concat.to_csv(f"{os.getenv('STATS_PATH')}/gw.csv")
    logging.info("Gameweek stats written to %s/gw.csv", os.getenv('STATS_PATH'))

    with open(f"{os.getenv('STATS_PATH')}/bootstrap_static.json", "w", encoding='ascii') as f:
        json.dump(bootstrap_static.data, f)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
