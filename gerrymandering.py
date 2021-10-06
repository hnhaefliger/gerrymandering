import gerrymandering
import json

gerrymander = gerrymandering.Gerrymander(path='PA2018.geojson')
gerrymander.init_districts(5)
gerrymander.start()
