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

        self.precincts = data.process_geojson(geojson)
        self.map = map.Map(self.precincts)
        self.prev_score = 0

    def init_districts(self, n):
        self.districts = [data.District(self.precincts[random.randint(0, len(self.precincts)-1)], i) for i in range(n)]
        expansions = [district.expand() for district in self.districts]

        while any(expansions):
            expansions = [district.expand() for district in self.districts]

        for district in self.districts:
            for precinct in district.precincts:
                self.map.set_precinct(precinct.name, district.color)   

    def score(self):
        target_vote = sorted([0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4])

        populations = [district.population for district in self.districts]
        #surface_area_to_perimeters = [district.surface_area_to_perimeter for district in self.districts]
        #distances = [district.avg_dist for district in self.districts]
        voters = sorted([district.dem / (district.dem + district.rep) for district in self.districts])

        # Lower is beter.
        population_score = 1 - 1 / (max(populations) - min(populations))
        #surface_area_to_perimeter_score = 1 / (sum(surface_area_to_perimeters) / len(surface_area_to_perimeters))
        #distance_score = 1 - 1 / (sum(distances) / len(distances))
        voter_score = sum([(voters[i] - target_vote[i])**2 for i in range(len(voters))]) / len(voters)
        
        return 0.3*population_score + voter_score# + 0.3 * distance_score# + 0.1*surface_area_to_perimeter_score

    def update(self):
        choices = []

        for district in self.districts:
            choices += district.neighbors

        choice = random.choice(choices)
        old_district = choice.district

        districts = [neighbor.district for neighbor in choice.neighbors if neighbor != choice.district]

        if districts:
            new_district = random.choice(districts)

            old_district.remove(choice)
            new_district.add(choice)

            self.map.set_precinct(choice.name, new_district.color)

            score = self.score()

            # Minimization of score
            if score > self.prev_score:
                if random.random() < 0.5:
                    new_district.remove(choice)
                    old_district.add(choice)

                    self.map.set_precinct(choice.name, old_district.color)

                else:
                    self.prev_score = score

            else:
                self.prev_score = score

        
    def loop(self, dt):
        self.update()
        self.map.after(dt, self.loop, dt)

    def start(self):
        self.map.mainloop()

        
        
