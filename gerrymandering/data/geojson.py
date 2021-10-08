from .precinct import Precinct
from tqdm import tqdm

def process_geojson(geojson):
    '''
    Reduce the json data down to it's useful fields.
    '''
    precincts = [Precinct(feature) for feature in tqdm(geojson['features'], desc='organizing precincts')]

    for i in tqdm(range(len(precincts)), desc='finding neighbors'):
        for j in range(i+1, len(precincts)):
            if precincts[i].neighboring(precincts[j]):
                precincts[i].neighbors.append(precincts[j])
                precincts[j].neighbors.append(precincts[i])

    return precincts
