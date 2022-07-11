import warnings
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
from HydroAcousticChart import HydroAcousticChart

#print(len(HydroAcousticChart("C:\Users\Юрий\Desktop\Vadim\материалы.220426\dat\521SHUM21.01.22\521SHUM21.01.22\NCH2_G_PO.bin\SK0_20220114_160213_830.bin".strip('"')).decode_bin().columns))
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
pd.options.plotting.backend = "plotly"
app = Dash(__name__)
fig2 = px.scatter()
# fig3 = px.line(df)
app.layout = html.Div(
    [
        html.H2(['Этот дэшборд построит графики для данных,', html.Br(), 'введите путь к файлу с данными в окно ниже'],
                style={'textAlign': 'center'}),

        html.Div([dcc.Input(
            id='input',
            type='text',
            placeholder='Путь к файлу')],
            style=dict(display='flex', justifyContent='center')),
        html.H3(id='ant', style={'textAlign': 'center'}),
        html.H3(['График максимальных значений в каналах ',
                 html.Br(),
                 'Нажмите на интересующий канал чтобы вывести график всех его измерений'],
                style={'textAlign': 'center'}),

        dcc.Graph(id='fig1'),

        html.H3(id='chnum', style={'textAlign': 'center'}),

        dcc.Graph(id='fig2'),

        # dcc.Graph(id = 'fig3', figure=fig3)
    ]
)


@app.callback(
    Output('ant', 'children'),
    Input('input', 'value')
)
def ant_inf(text):
    if text is None:
        raise PreventUpdate
    else:
        res = HydroAcousticChart(text.strip('"')).info()
    return f'Антенна: {res[0]} с количеством каналов {res[1]}'


@app.callback(
    Output('fig1', 'figure'),
    Input('input', 'value'))
def read_text(text):
    #file =
    if text is None:
        raise PreventUpdate
    else:
        ch_num = len(HydroAcousticChart(text.strip('"')).decode_bin().columns)
        print(ch_num)
        res = HydroAcousticChart(text.strip('"')).decode_bin()
        return px.bar(x=[i for i in range(1, ch_num+1)], y=res.max(axis=0),
                      labels={'x': 'Номер канала', 'y': 'Максимальное значение'})
        #return res.max(axis=0).plot(kind='bar')


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
     Input('input', 'value')])
def display_click_data(clickdata, text):
    if text is None:
        raise PreventUpdate
    else:
        df = HydroAcousticChart(text.strip('"')).decode_bin()
    if clickdata is not None:
        subset = clickdata['points'][0]['x']
        fig = px.line(df[subset],
                      labels={'value': 'Абсолютное значение', 'index': 'Номер измерения', 'variable': 'Номер канала'})
        return fig

    return fig2


if __name__ == '__main__':
    app.run_server(debug=True)
