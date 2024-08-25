import requests
import pandas as pd
import os

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


def main():
    df = buildLeagueDataFrame(os.getenv("LEAGUE_ID"))
    df = df.groupby("event").apply(calcPointsOffTop).reset_index(drop=True)
    df["team_value_mil"] = (df.value - df.bank)/10
    df["value_mil"] = df.value/10
    df["bank_mil"] = df.bank/10
    df.to_csv(f"{os.getenv('STATS_PATH')}/stats.csv")
    

if __name__ == "__main__":
    main()