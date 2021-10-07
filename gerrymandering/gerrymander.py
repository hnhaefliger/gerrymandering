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
                            choices[i] += self.data[c]['neighbors']
                            
                            # Don't remove duplicates as it promotes more cohesive starting districts.
                            # choices[i] = list(set(choices[i]))

                            break

                    else: break

            if all([len(choice)==0 for choice in choices]):
                break

        for i in range(n):
            for j in self.districts[i]:
                self.map.set_precinct(self.data[j]['loc, prec'], ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'cyan', 'pink'][i%8])                 

    def start(self):
        self.map.mainloop()

        
        
