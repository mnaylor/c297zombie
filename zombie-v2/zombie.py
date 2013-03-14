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

        if agentsim.debug.get(2):
            print("Zombie", self._name)

    def get_author(self):
        return "Your names go here"

    def compute_next_move(self):
        if agentsim.debug.get(128):
            pass
 
        delta_x = 100 * (0.5 - random.random())
        delta_y = 100 * (0.5 - random.random())
        return (delta_x, delta_y)
