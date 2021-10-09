import shapely.ops
import math
import random

class District:
    def __init__(self, base_precinct, i):
        base_precinct.district = self
        self.precincts = [base_precinct]
        self.neighbors = base_precinct.neighbors
        #self.shape = base_precinct.shape.buffer(1e-1)
        #self.perimeter = self.shape.length
        #self.area = self.shape.area
        self.i = i
        self.color = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'cyan', 'pink'][i % 8]

    def calculate_neighbors(self):
        self.neighbors = [neighbor for precinct in self.precincts for neighbor in precinct.neighbors if neighbor not in self.precincts]
    
    def add(self, other_precinct):
        other_precinct.district = self
        self.precincts.append(other_precinct)
        #self.shape = self.shape.union(other_precinct.shape.buffer(1e-1))
        #self.perimeter = self.shape.length
        #self.area = self.shape.area
        self.calculate_neighbors()

    def remove(self, other_precinct):
        other_precinct.district = None
        self.precincts.remove(other_precinct)
        #self.shape = shapely.ops.unary_union([precinct.shape.buffer(1e-1) for precinct in self.precincts])
        #self.perimeter = self.shape.length
        #self.area = self.shape.area
        self.calculate_neighbors()

    def expand(self):
        choices = [neighbor for neighbor in self.neighbors if neighbor.district == None]

        if choices:
            self.add(random.choice(choices))
            return True

        return False

    @property
    def surface_area_to_perimeter(self):
        return self.area / self.perimeter

    @property
    def population(self):
        return sum([precinct.population for precinct in self.precincts])

    @property
    def voters(self):
        return {
            'dem': sum([precinct.dem for precinct in self.precincts]),
            'rep': sum([precinct.rep for precinct in self.precincts]),
            'lib': sum([precinct.lib for precinct in self.precincts]),
            'gre': sum([precinct.gre for precinct in self.precincts]),
            'ind': sum([precinct.ind for precinct in self.precincts]),
        }

    @property
    def dem(self):
        return sum([precinct.dem for precinct in self.precincts])

    @property
    def rep(self):
        return sum([precinct.rep for precinct in self.precincts])

    @property
    def avg_dist(self):
        center = [
            sum([precinct.center[0] for precinct in self.precincts]) / len(self.precincts),
            sum([precinct.center[1] for precinct in self.precincts]) / len(self.precincts),
        ]

        distances = [math.sqrt((precinct.center[0] - center[0])** 2 + (precinct.center[1] - center[1])**2) for precinct in self.precincts]
        return sum(distances) / len(distances)

    
