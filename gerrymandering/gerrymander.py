from . import data
from . import map
import json
import random

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

    def init_districts(self, n):
        self.districts = []
        choices = []
        taken = []

        for i in range(n):
            self.districts.append(random.randint(0, len(self.data)-1))
            taken.append(self.districts[-1])
            choices.append(self.data[self.districts[-1]['neighbors']])

        c = self.districts[0][0]

        while len(taken) < len(self.data):
            for i in range(n):
                while True:
                    c = random.choice(choices)
                    choices[i].remove(c)
                    
                    if c not in taken:
                        taken.append(c)
                        self.districts[i].append(c)
                        choices[i] += self.data[c]['neighbors']
                        choices[i] = list(set(choices[i]))
                        break

        for i in range(n):
            for j in self.districts[i]:
                self.map.set_precinct(j, ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'cyan', 'pink'][i%8])                 

    def start(self):
        self.map.mainloop()

        
        
