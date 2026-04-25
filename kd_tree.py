from math import floor

Point = tuple[float, float]

class _KdNode:

    """

    Implements a 2D KD-Tree node

    Even levels are ordered by the X (first) component, while odd are ordered by the Y (second)

    """

    def __init__(self):
        self.value = None
        self.level = None
        self.point = None
        self.left_node = None
        self.right_node = None


    @classmethod
    def create_root(cls):
        out = cls()
        out.level = 0
        return out



class KdTree:

    """ 

    Impletments a 2D Kd-tree

    """

    def __init__(self, points: list[Point]):
        self._root = _KdNode.create_root()
        self._size = len(points)
        self._build_tree(points, self._root)

    
    def _split_points(self, points: list[Point], axis: int):
        half_length = floor(len(points) / 2)

        if len(points) == 1:
            return (points[0], points[0][axis], None)

        points.sort(key=lambda point: point[axis])
        if len(points) % 2 == 0:
            median = (points[half_length-1][axis] + points[half_length][axis]) / 2
        else: median = points[half_length][axis]
            
        return (points[:half_length], median, points[half_length:])


    def _build_tree(self, points: list[Point], node: _KdNode):
        if(len(points) == 0):
            raise ValueError("No points available")

        division = self._split_points(points, node.level % 2)
        node.value = division[1]

        if division[2] != None:
            node.left_node = _KdNode(level=node.level + 1)
            self._build_tree(division[0], node.left_node)

            node.right_node = _KdNode(level=node.level + 1)
            self._build_tree(division[2], node.right_node)
        else:
            node.point = division[0]

