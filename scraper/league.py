import requests
from dash import Dash, Input, Output, callback, html, dcc
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np

from func import getMatches, getPlayer
from static import BootstrapStatic

class League:
    base_url = 'https://fantasy.premierleague.com/api'
    
    def __init__(self, league: int, bootstrap_static: BootstrapStatic) -> None:
        self.league = league
        self.bootstrap_static = bootstrap_static
        
        r = requests.get(f"{self.base_url}/leagues-classic/{self.league}/standings/", timeout=5).json()
        df = pd.DataFrame(r["standings"]["results"])
        self.entries = df[["entry", "player_name"]]
    
    def getEntries(self) -> pd.DataFrame:
        return self.entries
    
    def __buildEntryTeam(self, entry: int) -> pd.DataFrame:
        current_gw = self.bootstrap_static.getCurrentGameweek()
        data = requests.get(f"{self.base_url}/entry/{entry['entry']}/event/{current_gw}/picks/", timeout=5).json()
        player_data = []
        for pick in data["picks"]:
            player = getPlayer(self.bootstrap_static.data, pick["element"])
            player["multiplier"] = pick["multiplier"]
            player["multiplied_event_points"] = pick["multiplier"] * player["event_points"]
            player["is_captain"] = pick["is_captain"]
            player["is_vice_captain"] = pick["is_vice_captain"]
            player_data.append(player)
        df = pd.DataFrame(player_data)
        return df[['web_name', 'multiplied_event_points', 'team', 'is_captain', 'is_vice_captain']]

    def getTeams(self) -> list[pd.DataFrame]:
        return [self.__buildEntryTeam(self.entries.loc[i]) for i in range(len(self.entries))]

    def buildGrid(self) -> dbc.Table:
        current_gw = self.bootstrap_static.getCurrentGameweek()
        matches_response = getMatches(current_gw=current_gw)
        table_header = [html.Thead(html.Tr([html.Th(self.entries.loc[i].player_name) for i in range(len(self.entries))]))]
        rows = []
        teams = self.getTeams()
        for i in range(len(teams[0])):
            cells = []
            for team in teams:
                player = team.loc[i]
                cell_class = ""
                for match in matches_response:
                    if player.team in (match["team_a"], match["team_h"]):
                        if match["started"] is False:
                            cell_class = "bg-light"
                        else:
                            if match["finished_provisional"] is True:
                                cell_class = "bg-info-subtle"
                            else:
                                cell_class = "bg-success text-white"
                        break
                captaincy = ""
                if player.is_captain is np.True_:
                    captaincy = " (c)"
                elif player.is_vice_captain is np.True_:
                    captaincy = " (vc)"
                cells.append(html.Td(
                    dbc.Container(dbc.Row([
                        dbc.Col(f"{player.web_name}{captaincy}", class_name="text-end"),
                        dbc.Col(f"{player.multiplied_event_points}", width=2)
                    ])), className=cell_class
                ))
            row = html.Tr(cells)
            rows.append(row)
        table_body = [html.Tbody(rows)]
        cells = []
        for team in teams:
            cells.append(html.Td(
                dbc.Container(dbc.Row([
                    dbc.Col("Total:", class_name="text-end"),
                    dbc.Col(f"{team.multiplied_event_points.sum()}", width=3)
                ])),
                className="fw-bold"
            ))
        foot = html.Tr(cells)
        return dbc.Table(table_header + table_body + [html.Tfoot(foot)], bordered=True)
    
    def getDataFrame(self):
        dataframes = []
        for i in range(len(self.entries)):
            r = requests.get(f"{self.base_url}/entry/{self.entries.iloc[i].entry}/history", timeout=5).json()
            df = pd.DataFrame(r["current"])
            df["entry"] = self.entries.iloc[i].entry
            df["player_name"] = self.entries.iloc[i].player_name
            dataframes.append(df)
        return pd.concat(dataframes, axis=0, ignore_index=True)
