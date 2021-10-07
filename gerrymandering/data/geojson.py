import math
#import numpy as np
#np.seterr(all='ignore')
from tqdm import tqdm

def unpack_polygons(array):
    '''
    Since we do not need groups we want all of the individual polygons in the precinct to be in the first level of the array.
    '''
    if isinstance(array[0][0], list):
        polygons = []

        for arr in array:
            polygon = unpack_polygons(arr)

            if isinstance(polygon[0], list):
                polygons += polygon

            else:
                polygons.append(polygon)

        return polygons

    else:
        return [i for j in array[:-1] for i in j[:2]]


def process_geojson(geojson):
    '''
    Reduce the json data down to it's useful fields.
    '''
    data = []

    for f, feature in tqdm(enumerate(geojson['features']), desc='organizing precincts'):
        data.append({
            'polygons': unpack_polygons(feature['geometry']['coordinates']),
            'neighbors': [],
            #'not_neighbors': [f],
        })

        data[-1].update(feature['properties'])

        all_coords = [i for j in data[-1]['polygons'] for i in j]

        # Speed up the calculation of neighbors.
        data[-1]['center'] = (sum(all_coords[::2])/len(all_coords) * 2, sum(all_coords[1:][::2])/len(all_coords) * 2)
        data[-1]['max_dist'] = 0

        for i in range(0, len(all_coords), 2):
            dist = (data[-1]['center'][0] - all_coords[i])**2 + (data[-1]['center'][1] - all_coords[i+1])**2
            if dist > data[-1]['max_dist']:
                data[-1]['max_dist'] = dist

        data[-1]['max_dist'] = math.sqrt(data[-1]['max_dist'])
        ###

    # Find all of the neighboring precincts.
    for i in tqdm(range(len(data)), desc='finding neighbors'):
        #data[i]['neighbors'], data[i]['not_neighbors'] = find_neighbors(data[i], data)
        data[i]['neighbors'] = find_neighbors(data[i], data)

    for i in tqdm(range(len(data)), desc='cleaning up'):
        del data[i]['max_dist']
        #del data[i]['not_neighbors']

    return data


def between(a, b, c):
    '''
    Check if c is between a and b.
    '''
    a, b = min((a, b)), max((a, b))
    return a <= c and b >= c

def slope(a, b, c, d):
    '''
    Calculate the slope of the line between (a, b) and (c, d).
    '''
    if c == a:
        return 10000

    else:
        return (d - b) / (c - a)

def intersecting_polygons(a, b):
    '''
    Calculate whether two polygons are touching
    '''
    # First we find any parallel edges in the two polygons.
    da = [slope(a[i], a[i+1], a[i+2], a[i+3]) for i in range(-2, len(a)-2, 2)]
    db = [slope(b[i], b[i+1], b[i+2], b[i+3]) for i in range(-2, len(b)-2, 2)]

    #a, b = np.array(a), np.array(b)

    #x, y = a[::2], a[1:][::2]
    #da = (np.roll(y, 1) - y) / (np.roll(x, 1) - x)

    #x, y = b[::2], b[1:][::2]
    #db = (np.roll(y, 1) - y) / (np.roll(x, 1) - x)

    for i, c in enumerate(da):
        for j in [i for i in range(len(db)) if abs(db[i] - c) < 1e-3]:#np.where(db == c)[0]:
            e, f = (i-1)*2, (j-1)*2
            w, x, y, z = a[e], a[e+1], a[e+2], a[e+3]
            s, t, u, v = b[f], b[f+1], b[f+2], b[f+3]

            # and then we check if all 4 points are colinear.
            if abs(slope(s, t, w, x) - c) < 1e-3:
                if (between(s, u, w) and between(t, v, x)) or (between(s, u, y) and between(t, v, z)):
                    return True

    return False


def find_neighbors(individual, group):
    '''
    Find all of the shapes that 'individual' is touching in the 'group'.
    '''
    index = group.index(individual)
    neighbors = []

    for i, member in enumerate(group):
        # This is actually slower than just doing the math because the lists grow over time.
        # if we already know that the two precincts are neighbors there is no need to recalculate intersections.
        #if index in member['neighbors']:
        #    neighbors.append(i)

        # if we already know that they are not neighbors then there is no need to recalculate intersections either.
        #elif index in member['not_neighbors']:
        #    not_neighbors.append(i)

        # now we check if they are actually close enough to be neighbors.
        if math.sqrt((individual['center'][0] - member['center'][0])**2 + (individual['center'][1] - member['center'][1])**2) <= member['max_dist'] + individual['max_dist']:
            # there is, of course, a copy of 'individual' in the group. (not necessary with not_neighbors)
            if individual != group[i]:
                b = False

                # for each of the polygons in both precincts.
                for individual_polygon in individual['polygons']:
                    for neighbor_polygon in group[i]['polygons']:
                        # if any of them are touching then there is no need to continue checking.
                        if intersecting_polygons(individual_polygon, neighbor_polygon):
                            neighbors.append(i)
                            b = True # we need to break both loops.

                        if b: break

                    if b: break

        #    # if there was never a match then there is no need to check again next time.
        #    if not(b):
        #        not_neighbors.append(i)

        # not neighbors is used to save time calculating future precincts.
        #else:
        #    not_neighbors.append(i)

    return neighbors#, not_neighbors


