import dash_leaflet as dl
from dash import Dash, Input, Output, State, callback, dcc, html

BH_CENTER = [-19.9191, -43.9386]

def register_layout(app: Dash):
    app.layout = html.Div(id="mapa-container", children=[

        # Mapa dash leaflet
        dl.Map(id="mapa", center=BH_CENTER, zoom=14, # type: ignore
               style={"width": "100%", "height": "100%"},
               children=[
                   dl.TileLayer(),
                   dl.LayerGroup(id="layer-markers"),  # Markers, atualiza com a kd_tree
               ]),

        # Painel principal
        html.Div(id="painel", children=[

            html.Div("Butecos-BH", id="painel-titulo"),

            # Inputs
            html.Div(className="campo", children=[
                html.Label("Endereço", htmlFor="input-endereco"),
                dcc.Input(id="input-endereco", type="text", placeholder="av. afonso pena, 1000"),
            ]),

            html.Div(className="campo", children=[
                html.Label("Diagonal (km)", htmlFor="input-diagonal"),
                dcc.Input(id="input-diagonal", type="number", placeholder="2.0", min=0.1, step=0.1),
            ]),

            html.Button("buscar", id="btn-buscar", n_clicks=0), # Butão que captura o estado dos inputs
        ]),
    ])


@callback(
    Output("layer-markers", "children"),  # Atualiza os markers no mapa
    Input("btn-buscar", "n_clicks"),      # Dispara ao clicar
    State("input-endereco", "value"),     # Lê o endereço sem disparar
    State("input-diagonal", "value"),     # Lê a diagonal sem disparar
    prevent_initial_call=True             # Não roda ao carregar a página
)
def buscar(n_clicks, endereco, diagonal):
    # Dispara a função do kd-tree
    print(" Campo ")
