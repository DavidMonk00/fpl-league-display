import requests

from static import BootstrapStatic

class Player:
    base_url = 'https://fantasy.premierleague.com/api'
    useful_stats = {
        1: ["minutes", "clean_sheets", "goals_conceded", "saves", "yellow_cards", "red_cards", "bonus", "bps"],
        2: ["minutes", "clean_sheets", "goals_conceded", "assists", "goals_scored", "defensive_contribution", "yellow_cards", "red_cards", "bonus", "bps"],
        3: ["minutes", "clean_sheets", "assists", "goals_scored", "defensive_contribution", "yellow_cards", "red_cards", "bonus", "bps"],
        4: ["minutes", "assists", "goals_scored", "defensive_contribution", "yellow_cards", "red_cards", "bonus", "bps"],
    }
    
    def __init__(self, element) -> None:
        self.element_id = element
    
    def getStaticInfo(self, bootstrap_static: BootstrapStatic = BootstrapStatic()) -> dict:
        return bootstrap_static.getPlayer(self.element_id)
    
    def getSummary(self) -> dict:
        return requests.get(f"{self.base_url}/element-summary/{self.element_id}", timeout=5).json()