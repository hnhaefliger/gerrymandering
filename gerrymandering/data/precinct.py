import math
import shapely.geometry
import shapely.ops

def unpack_polygons(geometry):
    '''
    Since we do not need groups we want all of the individual polygons in the precinct to be in the first level of the array.
    '''
    if geometry['type'] == 'Polygon':
        polygons = geometry['coordinates']

    elif geometry['type'] == 'MultiPolygon':
        polygons = [coordinates for polygon in geometry['coordinates']
                    for coordinates in polygon]

    else:
        raise TypeError('Invalid geometry.')

    polygons = [[coordinates[:2] for coordinates in polygon] for polygon in polygons]

    return polygons


def between(a, b, c):
    '''
    Check if c is between a and b.
    '''
    a, b = min((a, b)), max((a, b))
    return a <= c and b >= c


def slope(a, b):
    '''
    Calculate the slope of the line between a and b.
    '''
    if b[0] == a[0]:
        return 10000

    else:
        return (b[1] - a[1]) / (b[0] - a[0])


def intersecting_polygons(a, b):
    '''
    Calculate whether two polygons are touching
    '''
    # First we find any parallel edges in the two polygons.
    da = [slope(a[i-1], a[i]) for i in range(len(a))]
    db = [slope(b[i-1], b[i]) for i in range(len(b))]

    for i, c in enumerate(da):
        for j in [k for k in range(len(db)) if abs(db[k] - c) < 1e-2]:
            w, x, y, z = a[i-1], a[i], b[j-1], b[j]

            # and then we check if all 4 points are colinear.
            if abs(slope(w, y) - c) < 1e-2:
                if (between(w[0], x[0], y[0]) and between(w[1], x[1], y[1])) or (between(w[0], x[0], z[0]) and between(w[1], z[1], y[1])):
                    return True

    return False


class Precinct:
    def __init__(self, json):
        # for tkinter and neighbors
        self.polygons = unpack_polygons(json['geometry'])

        # to calculate metrics later
        self.shapes = [shapely.geometry.Polygon(coords) for coords in self.polygons]
        self.shape = shapely.ops.unary_union(self.shapes)

        # for reference
        self.name = json['properties']['loc, prec']

        # metrics
        self.dem = json['properties']['G18DemSen']
        self.rep = json['properties']['G18RepSen']
        self.lib = json['properties']['G18LibSen']
        self.gre = json['properties']['G18GreSen']
        self.ind = json['properties']['G18IndSen']
        self.population = self.dem + self.rep + self.lib + self.gre + self.ind

        self.neighbors = []
        self.district = None

        all_coords = [coords for polygon in self.polygons for coords in polygon]

        self.center = (
            sum([coords[0] for coords in all_coords]) / len(all_coords),
            sum([coords[1] for coords in all_coords]) / len(all_coords)
        )

        self.max_dist = 0
        for i in range(0, len(all_coords)):
            dist = (self.center[0] - all_coords[i][0])**2 + (self.center[1] - all_coords[i][1])**2
            if dist > self.max_dist:
                self.max_dist = dist
        self.max_dist = math.sqrt(self.max_dist)

    def neighboring(self, other):
        '''
        Determine if two precincts are neighbors.
        '''
        if math.sqrt((self.center[0] - other.center[0])**2 + (self.center[1] - other.center[1])**2) <= self.max_dist + other.max_dist:
            for polygon1 in self.polygons:
                for polygon2 in other.polygons:
                    if intersecting_polygons(polygon1, polygon2):
                        return True
        
        return False

    def tkinter(self):
        return [[coord for coords in polygon for coord in coords] for polygon in self.polygons]

        
