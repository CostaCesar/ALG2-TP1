from dash import Dash
from kd_tree import KdTree, Point
from interface import Interface
import csv

pontos = []
nomes  = {}

with open('../data/butecos_geocoded.csv', 'r') as f:
    for row in csv.reader(f, delimiter=';'):
        try:
            nome = row[0]
            lat  = float(row[1])
            lon  = float(row[2])
            pontos.append(Point(x=lat, y=lon))
            nomes[(lat, lon)] = nome
        except:
            continue

app = Dash(__name__, assets_folder="../assets/")
Interface(app, KdTree(pontos), nomes)

if __name__ == "__main__":
    print(f"Pontos carregados: {len(pontos)}")
    print(f"Nomes carregados: {len(nomes)}")
    app.run(debug=False)
