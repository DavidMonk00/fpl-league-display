from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import os

app = Dash(external_stylesheets=[dbc.themes.SANDSTONE])
server = app.server

def serve_layout():
    df = pd.read_csv(f"{os.getenv('STATS_PATH')}/stats.csv")
    df_table = df.copy()[df.event==df.event.max()][["player_name", "total_points"]]
    df_table = df_table.rename(columns={"player_name": "Player", "total_points": "Total Points"})

    layout = dbc.Container([
        html.H1('FPL Mini League Stats'),
        html.Hr(),
        dbc.Table.from_dataframe(df_table, bordered=True),
        
        dbc.Row([
            html.H2("Points")
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=px.bar(
                df, x='event', y='points', color='player_name', barmode='group', 
                labels={'event': 'Week', 'points': 'Gameweek Points', 'player_name': "Player"}
            ))),
            dbc.Col(dcc.Graph(figure=px.line(
                df, x='event', y='total_points', color='player_name',
                labels={'event': 'Week', 'total_points': 'Total Points', 'player_name': "Player"}
            )))
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=px.line(
                df, x='event', y='points_off_top', color='player_name',
                labels={'event': 'Week', 'points_off_top': 'Points Off Top', 'player_name': "Player"}
            ))),
            dbc.Col([
                dcc.Dropdown(["Mean", "Standard Deviation"], "Mean", id='average-points-dropdown-selection'),
                dcc.Graph(id="average-points-graph")
            ])     
        ]),
        dbc.Row([
            html.H2("Ranking")
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=px.bar(
                df, x='event', y='rank', color='player_name', barmode='group', log_y=True,
                labels={'event': 'Week', 'rank': 'Gameweek Rank', 'player_name': "Player"}
            ))),
            dbc.Col(dcc.Graph(figure=px.line(
                df, x='event', y='overall_rank', color='player_name', log_y=True,
                labels={'event': 'Week', 'overall_rank': 'Overall Rank', 'player_name': "Player"}
            )))
        ]),
        dbc.Row([
            html.H2("Finances")
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(["Total Value", "Team Value", "Bank"], "Total Value", id='finance-dropdown-selection'),
                dcc.Graph(id="finance-graph")
            ], width=6)
        ])
    ])
    return layout

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
            
app.layout = serve_layout

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
