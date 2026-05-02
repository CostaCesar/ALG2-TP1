import dash_leaflet as dl
from dash import Dash, Input, Output, State, callback, dcc, html
from geopy.geocoders import Nominatim
from geopy.distance import distance
from math import sqrt

BH_CENTER = [-19.9191, -43.9386]

ICON_CENTRO = {
    "iconpath": "../assets/marker-icon-red.png",
    "shadowpath": "../assets/marker-shadow.png",
    "iconSize": [25, 41],
    #"iconAnchor": [12, 41],
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

                # Seletor de modo:
                html.Div(id="campo", children=[
                    html.Label("Tipo de Busca:"),
                    dcc.RadioItems(id="radio-modo", options=['Quadrado','Círculo'], value='Quadrado', inline=True) # Seleciona o "modo" de busca.
                    ]),

                # Input do endereço:
                html.Div(className="campo", children=[
                    html.Label("Endereço", htmlFor="input-endereco"),
                    dcc.Input(id="input-endereco", type="text", placeholder="av. do contorno, 5057"), # O , é opcional
                ]),

                # Input da diagonal ou raio?
                html.Div(className="campo", children=[
                    html.Label("Diagonal (km)", id="label-dimensao", htmlFor="input-diagonal"),
                    dcc.Input(id="input-diagonal", type="number", placeholder="2.0", min=0.1, step=0.1), # Estranhamente, somente um step de 0.1 funciona
                ]),

                html.Button("buscar", id="btn-buscar", n_clicks=0),
            ]),
        ])


    def _create_markers(self, results, lat_centro, lon_centro):
        markers = [
            dl.Marker(
                position=(p.x, p.y), # type: ignore
                children=dl.Tooltip(self.nomes.get((p.x, p.y), "?"))
            ) for p in results if p
        ]

        # Adiciona o cento
        markers.append(dl.Marker(position=(lat_centro, lon_centro), icon=ICON_CENTRO)) # type: ignore
        return markers

    def find_circle(self, lat, lon, raio):

        raio_graus = raio / 111

        results = self.tree.search_in_circle((lat, lon), raio_graus)
        
        markers = self._create_markers(results, lat, lon)
        circle = dl.Circle(center=(lat, lon), radius=raio * 1000, color="red")
        return markers + [circle]

    def find_square(self, lat, lon, diagonal):
        
        lado = diagonal / sqrt(2)
        h_lado = lado / 2
        origem = (lat, lon)

        lat_max = distance(kilometers=h_lado).destination(origem, 0).latitude
        lat_min = distance(kilometers=h_lado).destination(origem, 180).latitude
        lon_max = distance(kilometers=h_lado).destination(origem, 90).longitude
        lon_min = distance(kilometers=h_lado).destination(origem, 270).longitude

        results = self.tree.search_in_rectangle((lat_min, lat_max), (lon_min, lon_max)) or []
        
        markers = self._create_markers(results, lat, lon)
        rect = dl.Rectangle(bounds=[[lat_min, lon_min], [lat_max, lon_max]], color="red") # type: ignore
        return markers + [rect]


    

    def _register_callbacks(self, app: Dash):

        @app.callback(
            Output("label-dimensao", "children"),
            Input("radio-modo", "value")
        )
        
        def update_label(modo):
            return "Raio (km)" if modo == "Círculo" else "Diagonal (km)"

        @app.callback(
            Output("layer-markers", "children"),  # Atualiza os markers no mapa
            Input("btn-buscar", "n_clicks"),      # Dispara ao clicar
            State("input-endereco", "value"),     # Lê o endereço sem disparar
            State("input-diagonal", "value"),     # Lê a diagonal sem disparar
            State("radio-modo", "value"),         # O modo de busca
            prevent_initial_call=True             # Impede disparo assim que abrir o site 
        )

        def search(n_clicks, endereco, valor, modo):
            if not endereco or not valor:
                return []

            location = self.convertor.geocode(f"{endereco}, Belo Horizonte, MG")
            if not location: return []
            
            lat, lon = location.latitude, location.longitude #type: ignore

            # Roteamento da lógica
            if modo == "Círculo":
                return self.find_circle(lat, lon, valor)
            else:
                return self.find_square(lat, lon, valor)


