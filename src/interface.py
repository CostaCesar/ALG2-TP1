import dash_leaflet as dl
from dash import Dash, Input, Output, State, callback, dcc, html
from geopy.geocoders import Nominatim
from geopy.distance import distance
from math import sqrt

BH_CENTER = [-19.9191, -43.9386]

ICON_CENTRO = {
    "iconUrl": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
    "shadowUrl": "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
    "iconSize": [25, 41],
    "iconAnchor": [12, 41],
} # Marker do centro


class Interface:

    def __init__(self, app: Dash, tree, nomes: dict):
        self.tree = tree
        self.nomes = nomes  # (lat, lon) -> nome do bar
        self.convertor = Nominatim(user_agent="SlaMundo")
        self._register_layout(app)
        self._register_callbacks(app)

    def _register_layout(self, app: Dash):
        app.layout = html.Div(id="mapa-container", children=[

            # Mapa principal
            dl.Map(id="mapa", center=BH_CENTER, zoom=14,  # type: ignore
                   style={"width": "100%", "height": "100%"},
                   children=[
                       dl.TileLayer(),
                       dl.LayerGroup(id="layer-markers"),  # Markers, são atualizados pelo callback
                   ]),

            # Painel flutuante
            html.Div(id="painel", children=[
                html.Div("Butecos-BH", id="painel-titulo"),

                html.Div(className="campo", children=[
                    html.Label("Endereço", htmlFor="input-endereco"),
                    dcc.Input(id="input-endereco", type="text", placeholder="av. do contorno, 5809"),
                ]),

                html.Div(className="campo", children=[
                    html.Label("Diagonal (km)", htmlFor="input-diagonal"),
                    dcc.Input(id="input-diagonal", type="number", placeholder="2.0", min=0.1, step=0.1),
                ]),

                html.Button("buscar", id="btn-buscar", n_clicks=0),
            ]),
        ])

    def _register_callbacks(self, app: Dash):

        @app.callback(
            Output("layer-markers", "children"),  # Atualiza os markers no mapa
            Input("btn-buscar", "n_clicks"),      # Dispara ao clicar
            State("input-endereco", "value"),     # Guarda o endereço
            State("input-diagonal", "value"),     # Guarda a diagonal
        )

        def buscar(n_clicks, endereco, diagonal):
            if not endereco or not diagonal:
                return []

            location = self.convertor.geocode(f"{endereco}, Belo Horizonte, MG")
            if location is None:
                print("Endereço não encontrado")
                return []

            lat = location.latitude   # type: ignore
            lon = location.longitude  # type: ignore

            lado  = diagonal / sqrt(2)
            h_lado = lado / 2

            # Extremos:

            origem = (lat, lon)
            lat_max = distance(kilometers=h_lado).destination(origem, bearing=0).latitude
            lat_min = distance(kilometers=h_lado).destination(origem, bearing=180).latitude
            lon_max = distance(kilometers=h_lado).destination(origem, bearing=90).longitude
            lon_min = distance(kilometers=h_lado).destination(origem, bearing=270).longitude


            # Obtendo os pontos que estão na área de interesse
            results = self.tree.search_in_rectangle(
                (lat_min, lat_max),
                (lon_min, lon_max)
            ) or []

            if results:
                p = results[0]

            # Markers dos bares com tooltip de nome
            markers = [
                dl.Marker(
                    position=(float(p.x), float(p.y)),                    # type: ignore
                    children=dl.Tooltip(self.nomes.get((p.x, p.y), "?")),
                )
                for p in results if p is not None
            ]

            # Marker do centro
            markers.append(dl.Marker(position=(lat, lon), icon=ICON_CENTRO))  # type: ignore

            # Retângulo da área de busca:
            rectangle = dl.Rectangle(
                bounds=((lat_min, lon_min), (lat_max, lon_max)),  # type: ignore
                color="red"
            )

            return markers + [rectangle]
