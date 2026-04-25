import dash_leaflet
from dash import Dash, html
from geopy.geocoders import Nominatim

from kd_tree import Point, KdTree

my_points = [(2,3),(5,4),(9,6),(4,7),(8,1)]
my_tree = KdTree(my_points)

print(my_tree)

