import pandas as pd
import requests
import json


def getBoostrapStatic(network=False) -> dict:
    base_url = 'https://fantasy.premierleague.com/api'
    if network is True:
        # print("Pulling data from API...")
        return requests.get(f"{base_url}/bootstrap-static", timeout=5).json()
    with open("bootstrap_static.json", "r", encoding="utf-8") as f:
        return json.load(f)


def getCurrentGameweek(bootstrap_static) -> int:
    events = bootstrap_static["events"]
    for event in events:
        if event["is_current"] is True:
            return event["id"]
    return -1


def getPlayer(bootstrap_static, player_id: int) -> dict:
    for element in bootstrap_static["elements"]:
        if element["id"] == player_id:
            return element
    return {}


def getProvisionalBonusPoints(match):
    bps = {}
    for stat in match["stats"]:
        if stat["identifier"] == "bps":
            bps = stat
            break
    players = bps["a"] + bps["h"]
    df = pd.DataFrame(players)
    df = df.sort_values(by=["value"], ascending=False, ignore_index=True)
    bonuses = []
    awarded = 0
    amount = 3
    current_value = 0
    for i in range(len(df)):
        if i == 0:
            d = df.iloc[i].to_dict()
            d["amount"] = amount
            current_value = d["value"]
            bonuses.append(d)
            awarded += 1
        elif awarded < 3:
            d = df.iloc[i].to_dict()
            if d["value"] == current_value:
                d["amount"] = amount
                amount -= 1
            else:
                amount -= 1
                d["amount"] = amount
            current_value = d["value"]
            bonuses.append(d)
            awarded += 1
        else:
            break
    return bonuses


def getTeam(bootstrap_static, code) -> dict:
    for team in bootstrap_static["teams"]:
        if team["id"] == code:
            return team
    return {}


def getStatLabel(bootstrap_static, name) -> str:
    for stat in bootstrap_static["element_stats"]:
        if name == stat['name']:
            return stat["label"]
    return ""


def getMatches(current_gw):
    base_url = 'https://fantasy.premierleague.com/api'
    return requests.get(f"{base_url}/fixtures/?event={current_gw}", timeout=5).json()


def isActive(network=False) -> bool:
    bootstrap_static = getBoostrapStatic(network=network)
    current_gw = getCurrentGameweek(bootstrap_static)
    active = False
    for match in getMatches(current_gw):
        if match["started"] is True and match["finished_provisional"] is False:
            active = True
    return active
