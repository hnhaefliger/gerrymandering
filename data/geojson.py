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

    return data
