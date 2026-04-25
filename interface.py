import dash_leaflet as dl
from dash import dcc, html, Dash

BH_CENTER = [-19.9191, -43.9386]

def register_layout(app: Dash):
    app.layout = html.Div(id="mapa-container", children=[

        dl.Map(id="mapa", center=BH_CENTER, zoom=14, # type: ignore
               style={"width": "100%", "height": "100%"},
               children=[dl.TileLayer(), dl.LayerGroup(id="layer-markers")]),

        html.Div(id="painel", children=[
            html.Div("belo horizonte · bares", id="painel-titulo"),
            html.Div(className="campo", children=[
                dcc.Input(id="input-endereco", type="text", placeholder="endereço"),
            ]),
            html.Div(className="campo", children=[
                dcc.Input(id="input-diagonal", type="number", placeholder="diagonal (km)", min=0.1, step=0.1),
            ]),
            html.Button("buscar", id="btn-buscar", n_clicks=0),
        ]),

    ])
