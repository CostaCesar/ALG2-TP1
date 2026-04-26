from dash import Dash
from kd_tree import KdTree, Point
import interface
import csv

pontos = []
with open('../data/butecos_geocoded.csv', 'r') as f:
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        try:
            #row[0]=nome, row[1]=lat, row[2]=lon
            pontos.append(Point(x=float(row[1]), y=float(row[2])))
        except: continue


tree = KdTree(pontos)
app = Dash(__name__, assets_folder="../assets/")

interface.register_layout(app, tree)

if __name__ == "__main__":
    app.run(debug=True)
