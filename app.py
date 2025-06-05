import dash
from dash import html, dcc, Input, Output, State
import dash_cytoscape as cyto
import pandas as pd

# CSV 불러오기
df = pd.read_csv("data.csv")

app = dash.Dash(__name__)
server = app.server

initial_elements = [{'data': {'id': 'ROOT', 'label': 'Skill Tree Root'}, 'classes': 'root'}]

teams = df['팀구분'].unique()
for team in teams:
    team_id = f"팀::{team}"
    initial_elements.append({'data': {'id': team_id, 'label': team}})
    initial_elements.append({'data': {'source': 'ROOT', 'target': team_id}})

app.layout = html.Div([
    html.H3("📘 Skill Tree (Drill-Down 방식)", style={'textAlign': 'center'}),
    cyto.Cytoscape(
        id='cytoscape',
        elements=initial_elements,
        layout={'name': 'breadthfirst', 'direction': 'LR'},
        style={'width': '100%', 'height': '850px'},
        stylesheet=[
            {'selector': 'node', 'style': {
                'label': 'data(label)',
                'background-color': '#636efa',
                'width': 25,
                'height': 25,
                'font-size': '11px'
            }},
            {'selector': '[url]', 'style': {
                'background-color': '#00cc96',
                'shape': 'ellipse'
            }},
            {'selector': '.root', 'style': {
                'background-color': '#EF553B',
                'shape': 'star'
            }},
            {'selector': 'edge', 'style': {
                'width': 2,
                'line-color': '#ccc'
            }},
        ]
    ),
    dcc.Store(id='stored-elements', data=initial_elements),
    dcc.Location(id='url', refresh=True)
])

@app.callback(
    Output('cytoscape', 'elements'),
    Output('stored-elements', 'data'),
    Input('cytoscape', 'tapNodeData'),
    State('stored-elements', 'data')
)
def expand_node(data, elements):
    if not data:
        return elements, elements
    node_id = data['id']
    new_elements = []
    if node_id.startswith("팀::"):
        team = node_id.split("::")[1]
        sub_df = df[df['팀구분'] == team]
        for proc in sub_df['공정'].unique():
            proc_id = f"공정::{team}::{proc}"
            if not any(e['data']['id'] == proc_id for e in elements if 'id' in e['data']):
                new_elements.append({'data': {'id': proc_id, 'label': proc}})
                new_elements.append({'data': {'source': node_id, 'target': proc_id}})
    elif node_id.startswith("공정::"):
        _, team, proc = node_id.split("::")
        sub_df = df[(df['팀구분'] == team) & (df['공정'] == proc)]
        for goal in sub_df['목표/방법'].unique():
            goal_id = f"목표::{team}::{proc}::{goal}"
            if not any(e['data']['id'] == goal_id for e in elements if 'id' in e['data']):
                new_elements.append({'data': {'id': goal_id, 'label': goal}})
                new_elements.append({'data': {'source': node_id, 'target': goal_id}})
    elif node_id.startswith("목표::"):
        _, team, proc, goal = node_id.split("::")
        sub_df = df[(df['팀구분'] == team) & (df['공정'] == proc) & (df['목표/방법'] == goal)]
        for _, row in sub_df.iterrows():
            tech = row['기술명']
            tech_id = f"기술::{team}::{proc}::{goal}::{tech}"
            if not any(e['data']['id'] == tech_id for e in elements if 'id' in e['data']):
                node_data = {'id': tech_id, 'label': tech}
                if pd.notnull(row.get('아이템 관련 자료', None)):
                    node_data['url'] = row['아이템 관련 자료']
                new_elements.append({'data': node_data})
                new_elements.append({'data': {'source': node_id, 'target': tech_id}})
    return elements + new_elements, elements + new_elements

@app.callback(Output('url', 'href'), Input('cytoscape', 'tapNodeData'))
def open_link(data):
    if data and 'url' in data:
        return data['url']
    return dash.no_update

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
