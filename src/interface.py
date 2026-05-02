import dash_leaflet as dl
from dash import Dash, dash_table, Input, Output, State, callback, dcc, html
from geopy.geocoders import Nominatim
from geopy.distance import distance
from math import sqrt

BH_CENTER = [-19.9191, -43.9386]

ICON_CENTRO = {
    "iconUrl": "/assets/marker-icon-red.png",
    "shadowUrl": "/assets/marker-shadow.png",
    "iconSize": [25, 41],
    "iconAnchor": [12, 41]
    }

class Interface:

    def __init__(self, app: Dash, tree, bar_data : dict):
        self.tree = tree
        self.bar_data = bar_data  # (lat, lon) -> nome do bar
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
                    dcc.RadioItems(id="radio-modo", options=['Quadrado','Círculo'], value='Quadrado', inline=True)
                    ]),

                # Input do endereço:
                html.Div(className="campo", children=[
                    html.Label("Endereço", htmlFor="input-endereco"),
                    dcc.Input(id="input-endereco", type="text", placeholder="av. do contorno, 5057"),
                ]),

                # Input da diagonal ou raio?
                html.Div(className="campo", children=[
                    html.Label("Diagonal (km)", id="label-dimensao", htmlFor="input-diagonal"),
                    dcc.Input(id="input-diagonal", type="number", placeholder="2.0", min=0.1, step=0.1),
                ]),

                html.Button("buscar", id="btn-buscar", n_clicks=0),
                ]),

            # Gaveta da tabela — botão à esquerda, expande para a direita
            html.Div(id="container-tabela", children=[
                html.Button("›", id="btn-toggle-tabela", n_clicks=0),
                html.Div(id="tabela-wrapper", children=[
                    html.Table(id="tabela-bares", children=[
                        html.Thead(html.Tr([html.Th("Nome"), html.Th("Endereço"), html.Th("Dist. (km)")])),
                        html.Tbody(id="tabela-corpo")
                    ])
                ]),
            ])

        ])


    def _create_markers(self, results, lat_centro, lon_centro):
        markers = [
            dl.Marker(
                position=(p.x, p.y), # type: ignore
                children=dl.Tooltip(self.bar_data.get((p.x, p.y), {}).get("name", "?"))
            ) for p in results if p
        ]

        # Adiciona o centro
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

        # Isso foi usado pra lidar com o fato de que a terra é uma superficie não euclidiana, é possível que isso não afete o programa, pois BH é pequeno em relação a terra.
        lat_max = distance(kilometers=h_lado).destination(origem, 0).latitude
        lat_min = distance(kilometers=h_lado).destination(origem, 180).latitude
        lon_max = distance(kilometers=h_lado).destination(origem, 90).longitude
        lon_min = distance(kilometers=h_lado).destination(origem, 270).longitude

        results = self.tree.search_in_rectangle((lat_min, lat_max), (lon_min, lon_max)) or []
        
        markers = self._create_markers(results, lat, lon)

        # Desenha o quadrado
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
            Output("layer-markers", "children"),
            Input("btn-buscar", "n_clicks"),
            State("input-endereco", "value"),
            State("input-diagonal", "value"),
            State("radio-modo", "value"),
            prevent_initial_call=True
        )
        def search(n_clicks, endereco, valor, modo):
            if not endereco or not valor:
                return []

            location = self.convertor.geocode(f"{endereco}, Belo Horizonte, MG")
            if not location: return []
            
            lat, lon = location.latitude, location.longitude #type: ignore

            if modo == "Círculo":
                return self.find_circle(lat, lon, valor)
            else:
                return self.find_square(lat, lon, valor)

        @app.callback(
            Output("tabela-wrapper", "className"),
            Output("btn-toggle-tabela", "children"),
            Input("btn-toggle-tabela", "n_clicks"),
        )

        def toggle_tabela(n_clicks):
            aberta = n_clicks % 2 == 1 # Verifica se ela está aberta(par) ou fechada(impar)
            return ("aberta", "‹") if aberta else ("", "›")

        @app.callback(
            Output("tabela-corpo", "children"),
            Input("btn-buscar", "n_clicks"),
            State("input-endereco", "value"),
            State("input-diagonal", "value"),
            State("radio-modo", "value"),
            prevent_initial_call=True
        )

        def atualiza_tabela(n_clicks, endereco, valor, modo):
            if not endereco or not valor:
                return []

            location = self.convertor.geocode(f"{endereco}, Belo Horizonte, MG") # Obtém a localização
            if not location:
                return []

            lat, lon = location.latitude, location.longitude #type: ignore

            # Obtém os pontos pelo modo:
            if modo == "Círculo":
                # Mesma lógica do círculo:
                results = self.tree.search_in_circle((lat, lon), valor / 111)
            else:
                # Mesma lógica do quadrado:
                lado = valor / sqrt(2)
                h = lado / 2
                origem = (lat, lon)
                lat_max = distance(kilometers=h).destination(origem, 0).latitude
                lat_min = distance(kilometers=h).destination(origem, 180).latitude
                lon_max = distance(kilometers=h).destination(origem, 90).longitude
                lon_min = distance(kilometers=h).destination(origem, 270).longitude
                results = self.tree.search_in_rectangle((lat_min, lat_max), (lon_min, lon_max)) or []

            # Ordena por ordem crescente os pontos:    
            rows = sorted([ # Ordena com base numa função de comparação
                {
                    "nome":     self.bar_data.get((p.x, p.y), {}).get("name", "?"),
                    "endereco": self.bar_data.get((p.x, p.y), {}).get("address", "?"),
                    "dist":     round(distance((lat, lon), (p.x, p.y)).km, 2)
                }
                for p in results if p
            ], key=lambda r: r["dist"]) # Compara pela distância.

            return [
                html.Tr([html.Td(r["nome"]), html.Td(r["endereco"]), html.Td(r["dist"])]) # Devolve as células
                for r in rows
            ]
