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
        '''
        with open('processed.json', 'r') as f:
            self.data = json.loads(f.read())
        '''

        self.map = map.Map(self.data)

    def init_districts(self, n):
        self.districts = []
        self.district_neighbors = []
        choices = []
        taken = []

        for i in range(n):
            self.districts.append([random.randint(0, len(self.data)-1)])
            taken.append(self.districts[-1][0])
            choices.append(self.data[self.districts[-1][0]]['neighbors'])

        c = self.districts[0][0]

        while len(taken) < len(self.data):
            for i in range(n):
                while True:
                    # Some districts might become locked in.
                    if choices[i]:
                        c = random.choice(choices[i])

                        # Remove multiple occurences.
                        choices[i] = [choice for choice in choices[i] if c != choice]
                        
                        # Could have been taken by a different district.
                        if c not in taken:
                            taken.append(c)
                            self.districts[i].append(c)
                            # Allowing duplicates promotes cohesive districts.
                            choices[i] += self.data[c]['neighbors']
                            self.data[c]['district'] = i

                            break

                    else: break

        for i in range(n):
            for j in self.districts[i]:
                self.map.set_precinct(self.data[j]['loc, prec'], ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'cyan', 'pink'][i%8])   

                self.district_neighbors += [neighbor for neighbor in self.data[j]['neighbors'] if neighbor not in self.district_neighbors and neighbor not in self.districts[i]]            

    def update(self):
        swap = random.choice(self.district_neighbors)
        choices = [self.data[neighbor]['district'] for neighbor in self.data[swap]['neighbors'] if self.data[swap]['district'] != self.data[neighbor]['district']]
        new_district = random.choice(choices)

        self.districts[self.data[swap]['district']].remove(swap)
        self.data[swap]['district'] = new_district
        self.districts[new_district].append(swap)
        self.map.set_precinct(self.data[swap]['loc, prec'], ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'cyan', 'pink'][new_district % 8])

        for neighbor in self.data[swap]['neighbors']:
            if any([self.data[sub_neighbor]['district'] != self.data[neighbor]['district'] for sub_neighbor in self.data[neighbor]['neighbors']]):
                if neighbor not in self.district_neighbors:
                    self.district_neighbors.append(neighbor)

            else:
                if neighbor in self.district_neighbors:
                    self.district_neighbors.remove(neighbor)
        
    def loop(self, dt):
        self.update()
        self.map.after(dt, self.loop, dt)

    def start(self):
        self.map.mainloop()

        
        
