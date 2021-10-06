import math
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
        return [i for j in array for i in j[:2]]


def process_geojson(geojson):
    '''
    Reduce the json data down to it's useful fields.
    '''
    data = []

    for feature in tqdm(geojson['features'], desc='organizing precincts'):
        data.append({
            'polygons': unpack_polygons(feature['geometry']['coordinates']),
            'neighbors': [],
            'not_neighbors': [],
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
        data[i]['neighbors'], data[i]['not_neighbors'] = find_neighbors(data[i], data)

    return data


def ccw(a, b, c, d, e, f):
    '''
    Based on https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
    '''
    return (f - b) * (c - a) > (d - b) * (e - a)


def intersecting_polygons(a, b):
    '''
    Calculate whether two polygons are touching
    '''
    # First we find any parallel edges in the two polygons.
    da = [(a[i+3] - a[i+1]) / (a[i+2] - a[i]) for i in range(-1, len(a)+1, 2)]
    db = [(b[i+3] - b[i+1]) / (b[i+2] - b[i]) for i in range(-1, len(a)+1, 2)]

    for i, c in enumerate(da):
        for j, d in enumerate(db):
            if c == d:
                # and then we check if they are touching.
                e, f = i*4, j*4
                w, x, y, z = a[e], a[e+1], a[e+2], a[e+3]
                s, t, u, v = b[f], b[f+1], b[f+2], b[f+3]

                if (ccw(w, x, s, t, u, v) != ccw(y, z, s, t, u, v)) and (ccw(w, x, y, z, s, t) != ccw(w, x, y, z, u, v)):
                    return True

    return False


def find_neighbors(individual, group):
    '''
    Find all of the shapes that 'individual' is touching in the 'group'.
    '''
    index = group.index(individual)
    neighbors = []
    not_neighbors = []

    for i, member in enumerate(group):
        # if we already know that the two precincts are neighbors there is no need to recalculate intersections.
        if index in member['neighbors']:
            neighbors.append(i)

        # if we already know that they are not neighbors then there is no need to recalculate intersections either.
        elif index in member['not_neighbors']:
            not_neighbors.append(i)

        # now we check if they are actually close enough to be neighbors.
        elif math.sqrt((individual['center'][0] - member['center'][0])**2 + (individual['center'][1] - member['center'][1])**2) <= member['max_dist'] + individual['max_dist']:
            # there is of course, a copy of 'individual' in the group.
            if member != individual:
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

                # if there was never a match then there is no need to check again next time.
                if not(b):
                    not_neighbors.append(i)

        # not neighbors is used to save time calculating future precincts.
        else:
            not_neighbors.append(i)

    return neighbors, not_neighbors


