from math import floor
from copy import deepcopy
from typing import NamedTuple

# Module classes

class Point:
    """
    Struct to hold point coordinates
    """

    def __init__(self, x: float = None, y: float = None):
        self.x = x
        self.y = y

    def get_coord(self, axis: int) -> float:
        """
        Where:
        axis = 0 -> X axis
        axis = 1 -> Y axis
        """

        if axis == 0:
            return self.x
        elif axis == 1:
            return self.y
        else:
            raise ValueError("Axis number must be either 0 or 1")



class Range(NamedTuple):
    """
    Struct to define a range of values 
    """
    min: float
    max: float



class Limit:
    """
    Struct to define a bounding box in (x,y) coordinates
    """

    def __init__(self):
        self.x: Range = None
        self.y: Range = None


    def get_coord(self, axis: int) -> float:
        """
        Where:
        axis = 0 -> X axis
        axis = 1 -> Y axis
        """
        if axis == 0:
            return self.x
        elif axis == 1:
            return self.y
        else:
            raise ValueError("Axis number must be either 0 or 1")
    


class _KdNode:
    """
    Implements a 2D KD-Tree node

    Even levels are ordered by the X (first) component, while odd are ordered by the Y (second)
    """

    # TODO: Reference to node's parent

    def __init__(self):
        self.bounds = None
        self.level = None
        self.point = None
        self.left_node = None
        self.right_node = None

    
    def is_leaf(self) -> bool:
        return self.left_node == None and self.right_node == None


    @classmethod
    def create_root(cls) -> Point:
        out = cls()
        out.level = 0
        return out



class KdTree:
    """ 
    Impletments a 2D Kd-tree

    The tree is built once by passing all the points as a list of "Point"
    """

    # TODO: KNN Search for spherical search

    def __init__(self, points: list[Point]):
        self._root = _KdNode.create_root()

        root_bounds = Limit()
        root_bounds.x = Range._make((min(point.x for point in points), max(point.x for point in points)))
        root_bounds.y = Range._make((min(point.y for point in points), max(point.y for point in points)))

        self._size = len(points)
        self._build_tree(points, self._root, root_bounds)

    
    def _split_points(self, points: list[Point], axis: int) -> tuple[list[Point], float, list[Point]]:
        half_length = floor(len(points) / 2)

        if len(points) == 1:
            return (points[0], points[0].get_coord(axis), None)

        points.sort(key=lambda point: point.get_coord(axis))
        if len(points) % 2 == 0:
            median = (points[half_length-1].get_coord(axis) + points[half_length].get_coord(axis)) / 2
        else: median = points[half_length].get_coord(axis)
            
        return (points[:half_length], median, points[half_length:])


    def _build_tree(self, points: list[Point], node: _KdNode, bounds: Limit):
        if len(points) == 0:
            raise ValueError("No points available")

        node.bounds = bounds
        axis = node.level % 2
        division = self._split_points(points, axis)

        left_bounds = deepcopy(bounds)
        right_bounds = deepcopy(bounds)

        if axis == 0:
            left_bounds.x = Range._make((bounds.x.min, division[1]))  
            right_bounds.x = Range._make((division[1], bounds.x.max)) 
        else:
            left_bounds.y = Range._make((bounds.x.min, division[1]))  
            right_bounds.y = Range._make((division[1], bounds.x.max)) 

        if division[2] != None:
            node.left_node = _KdNode()
            node.left_node.level = node.level + 1
            self._build_tree(division[0], node.left_node, left_bounds)

            node.right_node = _KdNode()
            node.right_node.level = node.level + 1
            self._build_tree(division[2], node.right_node, right_bounds)
        else:
            node.point = division[0]


    def _include_branch(self, node: _KdNode) -> list[_KdNode]:
        if node is None:
            return None    
        elif node.is_leaf():
            return [node]

        return self._include_branch(node.left_node) + [node] + self._include_branch(node.right_node)


    def _kd_search(self, node: _KdNode, limits: Limit) -> list[_KdNode]:
        if node is None:
            raise IndexError("Tree should not contain childless internal nodes")

        if node.is_leaf():
            if is_point_inside(node.point, limits):
                return [node]
            else: return []

        if is_limit_inside(node.bounds, limits):
            return _include_branch(node)

        axis = node.level % 2
        output = []

        if is_limit_intersect(node.left_node.bounds, limits): # node.value >= limits.get_coord(axis).min:
            output = output + self._kd_search(node.left_node, limits)

        if is_limit_intersect(node.right_node.bounds, limits): # node.value >= limits.get_coord(axis).min:
            output = output + self._kd_search(node.right_node, limits)

        return output


    def search_in_rectangle(self, x_limits: tuple[float, float], y_limits: tuple[float, float]) -> list[Point]:
        """
        x_limits: The min anbd max value of the X range, in that order.
        y_limits: The min anbd max value of the Y range, in that order.
        
        Returns: A list containing all points inside the bounding box (including the borders)
        """
        if self._size == 0:
            return None
        
        limits = Limit()
        limits.x = Range._make(sorted(x_limits))
        limits.y = Range._make(sorted(y_limits))

        node_list = self._kd_search(self._root, limits)

        return list(map(lambda node: node.point, node_list))



# Module Functions

def is_limit_inside(inner: Limit, outter: Limit) -> bool:
    if inner.x.min < outter.x.min or inner.x.max > outter.x.max:
        return False
    if inner.y.min < outter.y.min or inner.y.max > outter.y.max:
        return False
    
    return True


def is_point_inside(point: Point, limit: Limit) -> bool:
    if point.x < limit.x.min or point.x > limit.x.max:
        return False
    if point.y < limit.y.min or point.y > limit.y.max:
        return False
    
    return True


def tuple_to_point(point: tuple[float, float]) -> Point:
    return Point(point[0], point[1])


def is_limit_intersect(a: Limit, b: Limit) -> bool:
    if a.x.min <= b.x.max and b.x.min <= a.x.max:
        return True
    if a.y.min <= b.y.max and b.y.min <= a.y.max:
        return True
    
    return False
