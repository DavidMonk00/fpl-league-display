import os
from datetime import datetime
from dash import Dash, Input, Output, callback, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px

import pandas as pd

from func import getMatches, isActive
from league import League
from static import BootstrapStatic


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


def buildMatchScoreline(bootstrap_static: BootstrapStatic, match) -> dbc.Container:
    home_team = bootstrap_static.getTeam(match["team_h"])
    away_team = bootstrap_static.getTeam(match["team_a"])
    time = ""
    score = "v"
    score_style = "text-center"
    if match["started"] is True:
        score = f"{match['team_h_score']} - {match['team_a_score']}"
        time = f"{match['minutes']:02d}'" if match['finished_provisional'] is False else "FT"
        if match["finished_provisional"]:
            score_style += " bg-body-secondary"
        else:
            score_style += " bg-primary bg-opacity-50"
    return dbc.Container([dbc.Row([
        dbc.Col(html.Div(f"{time}"), width=2),
        dbc.Col(html.Div(f"{home_team['name']}", className="text-end")),
        dbc.Col(html.Div(score, className=score_style), width=1),
        dbc.Col(html.Div(f"{away_team['name']}")),
        dbc.Col(html.Div(), width=2)
    ])])


def buildMatchDetails(bootstrap_static: BootstrapStatic, match) -> dbc.Container:
    stat_rows = []
    for stat in match["stats"]:
        contributions = []
        max_contributions = max([len(stat['a']), len(stat['h'])])
        if max_contributions > 0:
            contributions.append(dbc.Col([html.H6(bootstrap_static.getStatLabel(stat["identifier"]), className="text-center")]))
            for i in range(max_contributions):
                try:
                    home_contribution = f"{bootstrap_static.getPlayer(stat['h'][i]['element'])['web_name']}" + (f" ({stat['h'][i]['value']})" if stat['h'][i]['value'] > 1 else "")
                except IndexError:
                    home_contribution = ""
                try:
                    away_contribution = (f"({stat['a'][i]['value']}) " if stat['a'][i]['value'] > 1 else "") + f"{bootstrap_static.getPlayer(stat['a'][i]['element'])['web_name']}"
                except IndexError:
                    away_contribution = ""
                contributions.append(dbc.Row([
                    dbc.Col(html.Div(home_contribution, className="text-end")),
                    dbc.Col(html.Div(), width=1),
                    dbc.Col(html.Div(away_contribution)),
                ]))
        
        stat_rows.append(dbc.Row(dbc.Container(contributions)))
    return dbc.Container(stat_rows)


def buildMatchesAccordionItems():
    bootstrap_static = BootstrapStatic()
    current_gw = bootstrap_static.getCurrentGameweek()
    matches_accordion_items = []
    for i, match in enumerate(getMatches(current_gw)):
        matches_accordion_items.append(dbc.AccordionItem(
            [buildMatchDetails(bootstrap_static, match)],
            title=buildMatchScoreline(bootstrap_static, match),
            item_id=f"matches-item-{i}"
        ))
    return matches_accordion_items

def buildLeagueTable():
    df = pd.read_csv(f"{os.getenv('STATS_PATH')}/stats.csv")
    df_table = df.copy()[df.event==df.event.max()][["player_name", "total_points"]]
    df_table = df_table.rename(columns={"player_name": "Player", "total_points": "Total Points"})
    return df_table


@callback(
    Output('live-update-text', 'children'),
    Input('interval-component', 'n_intervals')
)
def updateData(n):
    return f"Last updated: {datetime.now()}"


@callback(
    Output('live-update-active', 'children'),
    Input('interval-component', 'n_intervals')
)
def updateActiveBadge(n):
    if isActive(network=True):
        return "active"
    return ""


@callback(
    Output('matches-tab', 'children'),
    [Input('interval-component', 'n_intervals'), Input('matches-accordion', 'active_item')]
)
def updateMatchesTab(n, item):
    return dbc.Accordion(buildMatchesAccordionItems(), active_item=item, id="matches-accordion")


@callback(
    Output('teams-container', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def updateTeamsTab(n):
    league_id = int(os.getenv("LEAGUE_ID"))
    bootstrap_static = BootstrapStatic(network=True)
    league = League(league_id, bootstrap_static)
    return league.buildGrid()


@callback(
    Output('finance-graph', 'figure'),
    Input('finance-dropdown-selection', 'value')
)
def update_finance_graph(value):
    df = pd.read_csv(f"{os.getenv('STATS_PATH')}/stats.csv")
    match value:
        case "Total Value":
            dff = df[["value_mil", "player_name", "event"]]
            return px.line(
                dff, x='event', y='value_mil', color='player_name',
                labels={'event': 'Week', 'value_mil': 'Total Value (m)', 'player_name': "Player"}
            )
        case "Team Value":
            dff = df[["team_value_mil", "player_name", "event"]]
            return px.line(
                dff, x='event', y='team_value_mil', color='player_name',
                labels={'event': 'Week', 'team_value_mil': 'Team Value (m)', 'player_name': "Player"}
            )
        case "Bank":
            dff = df[["bank_mil", "player_name", "event"]]
            return px.line(
                dff, x='event', y='bank_mil', color='player_name',
                labels={'event': 'Week', 'bank_mil': 'Value (m)', 'player_name': "Player"}
            )
        case _:
            dff = df[["value_mil", "player_name", "event"]]
            return px.line(
                dff, x='event', y='value_mil', color='player_name',
                labels={'event': 'Week', 'value_mil': 'Total Value (m)', 'player_name': "Player"}
            )
            
@callback(
    Output('average-points-graph', 'figure'),
    Input('average-points-dropdown-selection', 'value')
)
def update_average_points_graph(value):
    df = pd.read_csv(f"{os.getenv('STATS_PATH')}/gw.csv")
    match value:
        case "Mean":
            return px.line(
                df, x="gw", y="mean", color="player_name",
                labels={"gw": "Week", "mean": "Mean Points per Player", 'player_name': "Player"}
            )
        case "Standard Deviation":
            return px.line(
                df, x="gw", y="std", color="player_name",
                labels={"gw": "Week", "std": "Standard Deviation", 'player_name': "Player"}
            )
        case _:
            return px.line(
                df, x="gw", y="mean", color="player_name",
                labels={"gw": "Week", "mean": "Mean Points per Player", 'player_name': "Player"}
            )


def serve_layout():
    bootstrap_static = BootstrapStatic()
    current_gw = bootstrap_static.getCurrentGameweek()
    
    tab1_content = dbc.Container(dbc.Accordion(buildMatchesAccordionItems(), start_collapsed=True, id="matches-accordion"), id="matches-tab")


    league_id = int(os.getenv("LEAGUE_ID"))
    league = League(league_id, bootstrap_static)
    tab2_content = dbc.Container(league.buildGrid(), id="teams-container")
    
    df = pd.read_csv(f"{os.getenv('STATS_PATH')}/stats.csv")
    tab3_content = dbc.Container([
        dbc.Table.from_dataframe(buildLeagueTable(), bordered=True),
        dbc.Row([
            html.H2("Points")
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=px.bar(
                df, x='event', y='points', color='player_name', barmode='group',
                labels={'event': 'Week', 'points': 'Gameweek Points', 'player_name': "Player"}
            )), width=6),
            dbc.Col(dcc.Graph(figure=px.line(
                df, x='event', y='total_points', color='player_name',
                labels={'event': 'Week', 'total_points': 'Total Points', 'player_name': "Player"}
            )), width=6)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=px.line(
                df, x='event', y='points_off_top', color='player_name',
                labels={'event': 'Week', 'points_off_top': 'Points Off Top', 'player_name': "Player"}
            )), width=6),
            dbc.Col(dbc.Container([
                dbc.Row(dcc.Dropdown(["Mean", "Standard Deviation"], "Mean", id='average-points-dropdown-selection')),
                dbc.Row(dcc.Graph(id="average-points-graph"))
            ]), width=6)
        ]),
        dbc.Row([
            html.H2("Ranking")
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=px.scatter(
                df, x='event', y='rank', color='player_name', log_y=True,
                labels={'event': 'Week', 'rank': 'Gameweek Rank', 'player_name': "Player"}
            )), width=6),
            dbc.Col(dcc.Graph(figure=px.line(
                df, x='event', y='overall_rank', color='player_name', log_y=True,
                labels={'event': 'Week', 'overall_rank': 'Overall Rank', 'player_name': "Player"}
            )), width=6)
        ]),
        dbc.Row([
            html.H2("Finances")
        ]),
        dbc.Row([
            dbc.Col(dbc.Container([
                dbc.Row(dcc.Dropdown(["Total Value", "Team Value", "Bank"], "Total Value", id='finance-dropdown-selection')),
                dbc.Row(dcc.Graph(id="finance-graph"))
            ]), width=6)
        ])
    ])

    tabs = dbc.Tabs(
        [
            dbc.Tab(tab1_content, label="Matches"),
            dbc.Tab(tab2_content, label="Teams"),
            dbc.Tab(tab3_content, label="Stats")
        ],
        active_tab="tab-0"
    )

    layout = dbc.Container([
        html.H4([f"Gameweek {current_gw} ", html.Span(id="live-update-active", className="badge bg-success")]),
        html.P("Last Updated: ", id="live-update-text"),
        tabs,
        dcc.Interval(
            id='interval-component',
            interval=10*1000, # in milliseconds
            n_intervals=0
        )
    ])
    return layout

app.layout = serve_layout


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
