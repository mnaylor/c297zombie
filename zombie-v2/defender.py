import random
import agentsim
from person import Person
from moveenhanced import MoveEnhanced

# Design note:
# The only reason for importing zombie and normal is to allow the class queries
# for zombies, normals such as
#   zombie.Zombie.get_all_instances()
# 
# If we used the import form:
#   from zombie import Zombie
# we would say
#   Zombie.get_all_instances()
# but this won't work because circular references would be created among 
# the three subclasses Zombies, Normals, and Defenders.  That is, the three
# classes are co-dependent in that they need to know that each other exists.

# The proper solution is that zombie, normal, defender would all be placed
# in the same module file to achieve the co-dependencies without the import.  
# But we want them in different files for the tournament.  There is never
# a good pure solution in the real world.

import zombie
import normal

def find_chosen(gravity):
    """
    This function takes a coordinate and finds the normal closest to it
    """
    min_grav = float("inf")
    chosen_one = None
    for n in normal.Normal.get_all_present_instances():
        location = (n.get_xpos(), n.get_ypos())
        priority = ((gravity[0] - location[0]) ** 2 + (gravity[1] - location[1]) ** 2) ** 0.5
        if priority < min_grav:
            min_grav = priority
            chosen_one = n

    return chosen_one.get_name()

def get_chosen_defenders():
    all_defenders = Defender.get_all_instances()
    chosen_defenders = []
    for i in all_defenders:
        if i.chosen_defender == True:
            chosen_defenders.append(i)
    return chosen_defenders
    
class Defender(MoveEnhanced):
    """
    Goes around attempting to prevent zombies form reaching normals
    """
    chosen_one = None
    chosen_defender = None

    def __init__(self, **keywords):
        MoveEnhanced.__init__(self, **keywords)

        if agentsim.debug.get(2):
            print("Defender", self._name)

    def get_author(self):
        return "Alexander Wong, Michelle Naylor"

    def get_defender_gravity(self):
        """
        This will get the center of gravity for all present defenders
        """
        # Change this to three defenders only closest to the gravity

        all_defenders = self.get_all_present_instances()
        # Find the average coordinates of all the defenders in the field
        count_defender = 0
        x_holder = 0
        y_holder = 0
        for i in all_defenders:
            if agentsim.debug.get(32):
                print("Defender: ", i.get_id(), i.get_xpos(), i.get_ypos())
            x_holder += i.get_xpos()
            y_holder += i.get_ypos()
            count_defender += 1
        x_holder = x_holder/count_defender
        y_holder = y_holder/count_defender
        gravity = (x_holder, y_holder)
        if agentsim.debug.get(32):
            print("Gravity: ", gravity)
        return gravity

    def create_chosen_defenders(self, gravity):
        """
        This function sets the chosen defender values for the three 
        defenders closest to the gravity equal to True, while the
        rest of the defenders are equal to zero

        This function should only modify values once per game
        Once chosen defenders are set, they are set for the duration 
        """
        all_defenders = self.get_all_present_instances()
        audition = []
        for i in all_defenders:
            gravity_dist = ((i.get_xpos() - gravity[0])**2 + (i.get_ypos() - gravity[1])**2) ** 0.5
            audition.append((i, gravity_dist))
        sorted(audition, key=lambda defender: defender[1]) # Sort by distance, lowest to highest
        # Take the first three (or less) defenders 
        # and make them the sacred chosen guardians
        
        for i in audition:
            if len(get_chosen_defenders()) == 3:
                break
            else:
                i[0].chosen_defender = True
        return
            
    def compute_next_move(self):
        delta_x = 0
        delta_y = 0

        # Find the gravity of the defenders
        our_gravity = self.get_defender_gravity()

        # Assign at most three defenders to be the chosen defenders
        # Take the three defenders closest to the gravity well
        if len(get_chosen_defenders()) == 0:
            self.create_chosen_defenders(our_gravity)
        
        # If we have no chosen one or our chosen one is a zombie,
        # find the new chosen one
        if (self.chosen_one == None):
            self.chosen_one = find_chosen(our_gravity)
        
        # Set the rough gravity location coordinates
        destination = (our_gravity[0] - self.get_xpos(), our_gravity[1] - self.get_ypos())
        # return destination
        
        # find nearest zombie if there is one!
        all_z = zombie.Zombie.get_all_present_instances()
        if all_z:
            nearest = min(
                # make pairs of (person, distance from self to person)
                [ (z, self.distances_to(z)[0] ) for z in all_z ]
                ,
                # and sort by distance
                key=(lambda x: x[1])
                )

            (near_z, near_d) = nearest

            # move towards nearest zombie
            (d, delta_x, delta_y, d_edge_edge) = self.distances_to(near_z)

            if agentsim.debug.get(64):
                print("nearest zombie to {} is {}, dx {} dy {}".format(
                    self.get_name(), near_z.get_name(), delta_x, delta_y, d_edge_edge))

            # but if close enough to teleport, send the zombie to a random
            # point instead
            if round(d_edge_edge, 3) <= self.get_teleport_threshold() :
                (x_min, y_min, x_max, y_max) = agentsim.gui.get_canvas_coords()
                x = random.randint(x_min, x_max)
                y = random.randint(y_min, y_max)
                self.teleport(near_z, x, y)

            # and change happiness proportional to distance
            (w,h) = agentsim.gui.get_canvas_size()
            diag = (w*w + h*h) ** .5
            delta_h = min( d/diag, .05)
            if agentsim.debug.get(64):
                print("d", d, "diag", diag, "dh", delta_h)

            self.set_happiness(delta_h + self.get_happiness())

        # alert the normals
        for n in normal.Normal.get_all_present_instances():
            for z in zombie.Zombie.get_all_present_instances():
                if n.is_near(z, 20) == True:
                    n.zombie_alert(z.get_xpos(), z.get_ypos())

        self.chosen_one.zombie_alert(our_gravity[0], our_gravity[1])
        # return (delta_x, delta_y)
        return destination
