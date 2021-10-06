import math

def unpack_polygons(array):
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
    data = []

    for feature in geojson['features']:
        data.append({
            'polygons': unpack_polygons(feature['geometry']['coordinates']),
        })

        data[-1].update(feature['properties'])

        all_coords = [i for j in data[-1]['polygons'] for i in j]
        data[-1]['center'] = (sum(all_coords[::2])/len(all_coords) * 2, sum(all_coords[1:][::2])/len(all_coords) * 2)
        data[-1]['max_dist'] = 0

        for i in range(0, len(all_coords), 2):
            dist = (data[-1]['center'][0] - all_coords[i])**2 + (data[-1]['center'][1] - all_coords[i+1])**2
            if dist > data[-1]['max_dist']:
                data[-1]['max_dist'] = dist

        data[-1]['max_dist'] = math.sqrt(data[-1]['max_dist'])

    for i in range(len(data)):
        data[i]['neighbors'] = find_neighbors(data[i], data)

    return data

def determinant(a, b):
    return a[0] * b[1] - a[1] * b[0]


def intersecting(a, b, c, d):
    try:
        det = determinant([b[0]-a[0], b[1]-a[1]], [c[0]-d[0], c[1]-d[1]])
        t = determinant([c[0]-a[0], c[1]-a[1]], [c[0]-d[0], c[1]-d[1]]) / det
        u = determinant([b[0]-a[0], b[1]-a[1]], [c[0]-a[0], c[1]-a[1]]) / det

        if t < 0 or u < 0 or t > 1 or u > 1:
            return False
        
        else:
            return True

    except ZeroDivisionError:
        return True


def intersecting_polygons(a, b):
    a = [[a[i], a[1+1]] for i in range(0, len(a), 2)]
    b = [[b[i], b[1+1]] for i in range(0, len(b), 2)]

    for i in range(-1, len(a)):
        for j in range(-1, len(b)):
            if intersecting(a[i], a[i+1], b[i], b[i+1]):
                return True


def find_neighbors(individual, group):
    potential_neighbors = []

    for i, member in enumerate(group):
        if math.sqrt((individual['center'][0] - member['center'][0])**2 + (individual['center'][1] - member['center'][1])**2) <= member['max_dist'] + individual['max_dist']:
            if member != individual:
                potential_neighbors.append(i)

    neighbors = []

    for neighbor in potential_neighbors:
        b = False

        for individual_polygon in individual['polygons']:
            for neighbor_polygon in group[neighbor]['polygons']:
                if intersecting_polygons(individual_polygon, neighbor_polygon):
                    neighbors.append(neighbor)
                    b = True

                if b: break

            if b: break

    return neighbors


