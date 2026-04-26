import dash_leaflet as dl
import time
from dash import Dash, Input, Output, State, callback, dcc, html
from geopy.geocoders import Nominatim
from geopy.distance import distance
from math import sqrt

BH_CENTER = [-19.9191, -43.9386]
convertor = Nominatim(user_agent="SlaMundo") # Converte os endereços em coordenadas

app_tree = None

def register_layout(app: Dash, tree):
    global app_tree
    app_tree = tree

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
    time.sleep(1)
    if not endereco or not diagonal: return []
    location = convertor.geocode(f"{endereco}, Belo Horizonte, MG")
    
    if location is None:
        print("Endereço não pode ser resolvido")
        return []

    lat = location.latitude #type: ignore
    lon = location.longitude #type: ignore

    lado = diagonal / sqrt(2) # Não ficou claro pela especificação, então fiz como centro da diagonal
    h_lado = lado / 2 # metade do lado

    origem = (lat, lon)

    north = distance(kilometers=h_lado).destination(origem, bearing=0)
    south = distance(kilometers=h_lado).destination(origem, bearing=180)
    east  = distance(kilometers=h_lado).destination(origem, bearing=90)
    west  = distance(kilometers=h_lado).destination(origem, bearing=270)

    lat_min = south.latitude
    lat_max = north.latitude
    lon_min = west.longitude
    lon_max = east.longitude

    results = app_tree.search_in_rectangle( # type: ignore
        (lat_min, lat_max),
        (lon_min, lon_max)
    )

    if not results:
        return [dl.Marker(position=(lat, lon))] # type: ignore

    # Markers dos bares encontrados
    markers = [
            dl.Marker(position=[float(p.x), float(p.y)]) # type: ignore
        for p in results if p is not None
    ]

    # Marker do endereço buscado
    markers.append(dl.Marker(position=[lat, lon])) # type: ignore

    # Retângulo da área de busca
    rectangle = dl.Rectangle(
        bounds=[[lat_min, lon_min], [lat_max, lon_max]], # type: ignore 
        color="red"
    )

    return markers + [rectangle]


