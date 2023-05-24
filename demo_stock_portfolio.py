"""
This app is for Alpha version 2.0.0a5

pip install dash-ag-grid==2.0.0a5

"""


import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

equities = {
    "RO.SW": "Roche Holding AG",
    "EMMN.SW": "Emmi AG",
    "HUBN.SW": "Huber+Suhner AG",
    "NOVN.SW": "Novartis AG",
    "BUCN.SW": "Bucher Industries AG",
    "AMS.SW": "ams-OSRAM AG ",
    "ZEHN.SW": "Zehnder Group AG",
    "ZWM.SW": "Zwahlen & Mayr SA ",
    "VETN.SW": "Vetropack Holding AG",
    "VBSN.SW": "IVF Hartmann Holding AG",
    "TIBN.SW": "Bergbahnen Engelberg-Trübsee-Titlis AG",
    "STRN.SW": "Schlatter Industries AG ",
    "STGN.SW": "Starrag Group Holding AG",
    "PEDU.SW": "Perrot Duval Holding S.A.",
    "OFN.SW": "Orell Füssli AG",
    "METN.SW": "Metall Zug AG",
    "HREN.SW": "Romande Energie Holding SA", 
    "HOLN.SW": "Holcim Ltd",
    "GMI.SW": "Groupe Minoteries SA",
    "CICN.SW": "Cicor Technologies Ltd.",
    "ADVN.SW": "Adval Tech Holding AG"

}


def get_stock_data():
    return yf.download(tickers=list(equities.keys()), period="5y", group_by="ticker")


stock_data = get_stock_data()


def last_close(ticker):
    return stock_data[ticker]["Close"].iloc[-1]


data = {
    "ticker": [ticker for ticker in equities],
    "company": [name for name in equities.values()],
    "quantity": [6, 4, 40, 25, 8, 410, 47, 12, 54, 19, 51, 118, 35, 25, 22, 1, 2, 48, 7, 62, 37],
    "price": [last_close(ticker) for ticker in equities],
    "comments": ["Notes" for i in range(21)],
}
df = pd.DataFrame(data)


columnDefs = [
    {
        "headerName": "Stock Ticker",
        "field": "ticker",
    },
    {
        "headerName": "Company",
        "field": "company",
    },
    {
        "headerName": "Shares",
        "field": "quantity",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "editable": True,
    },
    {
        "headerName": "Last Close Price",
        "field": "price",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
        "cellRenderer": "agAnimateShowChangeCellRenderer",
    },
    {
        "headerName": "Market Value",
        "type": "rightAligned",
        "filter": "agNumberColumnFilter",
        "valueGetter": {"function": "Number(params.data.price) * Number(params.data.quantity)"},
        "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
        "cellRenderer": "agAnimateShowChangeCellRenderer",
    },
#    {
 #       "headerName": "Position",
 #       "field": "position",
 #       "editable": True,
 #       "cellEditor": "agSelectCellEditor",
 #       "cellEditorParams": {
 #           "values": ["buy", "sell", "hold"],
 #       },
 #   },
    {
        "headerName": "Comments",
        "field": "comments",
        "editable": True,
        "cellEditorPopup": True,
        "cellEditor": "agLargeTextCellEditor",
    },
]

#cellStyle = {
#    "styleConditions": [
#        {
#            "condition": "params.value == 'buy'",
#            "style": {"backgroundColor": "#196A4E", "color": "white"},
#        },
#        {
#            "condition": "params.value == 'sell'",
#            "style": {"backgroundColor": "#800000", "color": "white"},
#        },
#        {
#            "condition": "params.colDef.headerName == 'Shares'",
#            "style": {"backgroundColor": "#444"},
#        },
# ]
#}

defaultColDef = {
    "filter": True,
    "resizable": True,
    "sortable": True,
    "editable": False,
    "floatingFilter": True,
    "minWidth": 125,
#    "cellStyle": cellStyle,
}


grid = dag.AgGrid(
    id="portfolio-grid",
    className="ag-theme-alpine-dark",
    columnDefs=columnDefs,
    rowData=df.to_dict("records"),
    columnSize="sizeToFit",
    defaultColDef=defaultColDef,
    dashGridOptions={"undoRedoCellEditing": True, "rowSelection": "single"},
)

candlestick = dbc.Card(dcc.Graph(id="candlestick"), body=True)
pie = dbc.Card(dcc.Graph(id="asset-allocation"), body=True)
header = html.Div("Hemdsärmlig Asset Management", className="h2 p-2 text-white bg-primary text-center")

app.layout = dbc.Container(
    [
        header,
        dbc.Row([dbc.Col(candlestick), dbc.Col(pie)]),
        dbc.Row(dbc.Col(grid, className="py-4")),
    ],
)

grid = dag.AgGrid(
    id="portfolio-grid",
    className="ag-theme-alpine-dark",
    columnDefs=columnDefs,
    rowData=df.to_dict("records"),
    columnSize="sizeToFit",
    defaultColDef=defaultColDef,
    dashGridOptions={"undoRedoCellEditing": True, "rowSelection": "single"},
)



@app.callback(
    Output("candlestick", "figure"),
    Input("portfolio-grid", "selectedRows"),
)
def update_candlestick(selected_row):
    if selected_row is None:
        ticker = "RO.SW"
        company = "Roche"
    else:
        ticker = selected_row[0]["ticker"]
        company = selected_row[0]["company"]

    dff_ticker_hist = stock_data[ticker].reset_index()
    dff_ticker_hist["Date"] = pd.to_datetime(dff_ticker_hist["Date"])

    fig = go.Figure(
        go.Candlestick(
            x=dff_ticker_hist["Date"],
            open=dff_ticker_hist["Open"],
            high=dff_ticker_hist["High"],
            low=dff_ticker_hist["Low"],
            close=dff_ticker_hist["Close"],
        )
    )
    fig.update_layout(
        title_text=f"{ticker} {company} Daily Price", template="plotly_dark"
    )
    return fig


@app.callback(
    Output("asset-allocation", "figure"),
    Input("portfolio-grid", "cellValueChanged"),
    State("portfolio-grid", "rowData"),
)
def update_portfolio_stats(_, data):
    dff = pd.DataFrame(data)
    dff["total"] = dff["quantity"].astype(float) * dff["price"].astype(float)
    portfolio_total = dff["total"].sum()

    return px.pie(
        dff,
        values="total",
        names="ticker",
        hole=0.3,
        title=f"Portfolio Total CHF {portfolio_total:,.2f}",
        template="plotly_dark",
    )



if __name__ == "__main__":
    app.run_server(debug=True, port=8060)