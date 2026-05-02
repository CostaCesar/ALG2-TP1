from dash import Dash
from kd_tree import KdTree, Point
from interface import Interface
import csv

pontos = []
bar_data = {} # ponto -> {nome do bar, endereço} 

with open('../data/butecos_geocoded.csv', 'r') as f:
    for row in csv.reader(f, delimiter=';'):
        try:
            address = row[0]
            name = row[1]
            lat  = float(row[2])
            lon  = float(row[3])
            pontos.append(Point(x=lat, y=lon))
            bar_data[(lat, lon)] = {"name": name, "address": address}
        except:
            continue

app = Dash(__name__, assets_folder="../assets/")
Interface(app, KdTree(pontos), bar_data)

if __name__ == "__main__":
    print(f"Pontos carregados: {len(pontos)}") # Debug
    app.run(debug=False)
