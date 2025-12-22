import json
import logging
import os

import requests


class BootstrapStatic:
    def __init__(self, network=False) -> None:
        self.network = network
        base_url = 'https://fantasy.premierleague.com/api'
        if network is True:
            logging.debug("Pulling data from API...")
            self.data = requests.get(f"{base_url}/bootstrap-static", timeout=5).json()
        else:
            with open(os.getenv("BOOTSTRAP_STATIC_PATH", ".") + "/bootstrap_static.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)

    def getCurrentGameweek(self) -> int:
        events = self.data["events"]
        for event in events:
            if event["is_current"] is True:
                return event["id"]
        return -1

    def getStatLabel(self, name) -> str:
        for stat in self.data["element_stats"]:
            if name == stat['name']:
                return stat["label"]
        return ""

    def getPlayer(self, player_id: int) -> dict:
        for element in self.data["elements"]:
            if element["id"] == player_id:
                return element
        return {}
    
    def getTeam(self, code) -> dict:
        for team in self.data["teams"]:
            if team["id"] == code:
                return team
        return {}
