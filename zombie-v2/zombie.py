import random
import agentsim
from person import Person
from moveenhanced import MoveEnhanced

# co-dependent imports
import normal
import defender

class Zombie(MoveEnhanced):

    def __init__(self, **keywords):
        MoveEnhanced.__init__(self, **keywords)
        self.set_happiness(1)
        
        self._default_size = self.get_size()

        if agentsim.debug.get(2):
            print("Zombie", self._name)

    def get_author(self):
        return "Alexander Wong, Michelle Naylor"


    def compute_next_move(self):
        if agentsim.debug.get(128):
            pass
        delta_x = 0
        delta_y = 0

        # make sure you are your normal size
        self.set_size(self._default_size)

        # find nearest normal if there is one!
        all_n = normal.Normal.get_all_present_instances()
        if all_n:
            nearest = min(
                # make pairs of (person, distance from self to person)
                [ (n, self.distances_to(n)[0] ) for n in all_n ]
                ,
                # and sort by distance
                key=(lambda x: x[1])
                )

            (near_n, near_d) = nearest

            # move towards nearest normal
            (d, delta_x, delta_y, d_edge_edge) = self.distances_to(near_n)

            # if close to target, get bigger
            if d < 65:
                old_size = self.get_size()
                max_size = self.get_max_size()
                self.set_size(max_size)

        return (delta_x, delta_y)
