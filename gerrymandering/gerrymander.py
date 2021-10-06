from . import data
from . import map
import json

class Gerrymander:
    def __init__(self, path=None, state=None):
        assert(state != None or path != None)

        if path:
            with open(path, 'r') as f:
                geojson = json.loads(f.read())

        elif state:
            geojson = data.get_state_geojson(state).json()

        self.data = data.process_geojson(geojson)
        self.map = map.Map(self.data)

    def start(self):
        self.map.mainloop()

        
        
