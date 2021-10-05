'''
Download state data from openprecincts.org.
'''
import requests
import re
import warnings

def get_state_html(state):
    '''
    Get state homepage.
    '''
    with warnings.catch_warnings():  # hide verification warning
        warnings.simplefilter("ignore")
        response = requests.get(f'https://openprecincts.org/{state}/', verify=False, headers={'User-Agent': 'gerrymandering.py'})

    return response.content.decode('utf-8')


def get_state_shapefile_url(state):
    '''
    Return the url to download the openprecincts shapefile for a given state.
    '''
    file = re.findall('"zip_file_id": "*(.+?)"', get_state_html(state))[0]
    return f'https://openprecincts.org/files/download/{file}/'


def get_state_geojson_url(state):
    '''
    Return the url to download the openprecincts geojson for a given state.
    '''
    file = re.findall('"geojson_file_id": "*(.+?)"', get_state_html(state))[0]
    return f'https://openprecincts.org/files/download/{file}/'


def get_state_shapefile(state):
    '''
    Return the contents of a given state's shapefile.
    '''
    with warnings.catch_warnings():  # hide verification warning
        warnings.simplefilter("ignore")
        return requests.get(get_state_shapefile_url(state), verify=False, headers={'User-Agent': 'gerrymandering.py'}).content


def get_state_geojson(state):
    '''
    Return the contents of a given state's geojson.
    '''
    with warnings.catch_warnings():  # hide verification warning
        warnings.simplefilter("ignore")
        return requests.get(get_state_geojson_url(state), verify=False, headers={'User-Agent': 'gerrymandering.py'}).content


#https: // openprecincts.org/files/download/1f0a3612-78d2-413f-acbc-15289e4e7db7
