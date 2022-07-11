from pathlib import Path
import base64
import warnings
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from HydroAcousticChart import HydroAcousticChart

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
pd.options.plotting.backend = "plotly"
app = Dash(__name__)
fig2 = px.scatter()

app.layout = html.Div(
    [
        html.H2(['Этот дэшборд построит графики для данных,',
                 html.Br(),
                 'введите путь к файлу с данными в окно ниже'],
                style={'textAlign': 'center'}),

        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Перетащите или ',
                html.A('выберите файл')
            ]),
            style={
                'width': '30%',
                'height': '60px',
                'lineHeight': '60px',
                'borderColor': 'maroon',
                'borderWidth': '5px',
                'borderStyle': 'solid',
                'justifyContent': 'center',
                'text-align': 'center',
                'borderRadius': '20px',
                'margin': 'auto'
            },
            multiple=True
        ),
        html.H3(id='ant', style={'textAlign': 'center'}),
        html.H3(['График максимальных значений в каналах ',
                 html.Br(),
                 'Нажмите на интересующий канал чтобы вывести график всех его измерений'],
                style={'textAlign': 'center'}),

        dcc.Graph(id='fig1'),

        html.H3(id='chnum', style={'textAlign': 'center'}),
        dcc.Graph(id='fig2')
    ])


@app.callback(
    Output('ant', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified'))
def ant_inf(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is None:
        raise PreventUpdate
    else:
        res = HydroAcousticChart(base64.b64decode(list_of_contents[0].split(',')[1])).info_upload()

    return f'Антенна: {res[0]} с количеством каналов {res[1]}'


@app.callback(Output('fig1', 'figure'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is None:
        raise PreventUpdate
    else:
        res = HydroAcousticChart(base64.b64decode(list_of_contents[0].split(',')[1])).decode_upload()
        ch_num = len(res.columns)
        return px.bar(x=[i for i in range(1, ch_num + 1)], y=res.max(axis=0),
                      labels={'x': 'Номер канала', 'y': 'Максимальное значение'})


@app.callback(
    Output('chnum', 'children'),
    Input('fig1', 'clickData'))
def channel_num(clickdata):
    if clickdata is not None:
        subset = clickdata['points'][0]['x']
        return f'График всех измерений для канала №{subset}'


@app.callback(
    Output('fig2', 'figure'),
    [Input('fig1', 'clickData'),
     Input('upload-data', 'contents'),
     State('upload-data', 'filename'),
     State('upload-data', 'last_modified')])
def display_click_data(clickdata, list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is None:
        raise PreventUpdate
    else:
        df = HydroAcousticChart(base64.b64decode(list_of_contents[0].split(',')[1])).decode_upload()
    if clickdata is not None:
        subset = clickdata['points'][0]['x']
        fig = px.line(df[subset],
                      labels={'value': 'Абсолютное значение', 'index': 'Номер измерения', 'variable': 'Номер канала'})
        return fig

    return fig2


if __name__ == '__main__':
    app.run_server(debug=True)
