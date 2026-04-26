import dash_leaflet
from dash import Dash, html
from geopy.geocoders import Nominatim

from kd_tree import Point, KdTree

my_points = [Point(5, 5), Point(2, 3), Point(8, 1), Point(9, 6), Point(4, 7), Point(1, 1), Point(7, 4), Point(3, 9), Point(6, 2), Point(10, 8)]
my_tree = KdTree(my_points)

result = my_tree.search_in_rectangle((4,8), (1,5))
print(result)

result = my_tree.search_in_circle((5,5), 3)
print(result)

