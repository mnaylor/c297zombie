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

    return chosen_one

class Defender(MoveEnhanced):
    """
    Goes around attempting to prevent zombies form reaching normals
    """
    chosen_one = None
    chosen_defender = False

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
            self.chosen_defender = True
            print(i.get_id(), i.get_xpos(), i.get_ypos())
            x_holder += i.get_xpos()
            y_holder += i.get_ypos()
            count_defender += 1
            
        x_holder = x_holder/count_defender
        y_holder = y_holder/count_defender
        gravity = (x_holder, y_holder)
        print(gravity)
        return gravity
        

    def compute_next_move(self):
        delta_x = 0
        delta_y = 0
        
        # Find the gravity of the defenders
        our_gravity = self.get_defender_gravity()
        
        # If we have no chosen one or our chosen one is a zombie,
        # find the new chosen one
        if (self.chosen_one == None):
            # Find the chosen normal to be protected
            self.chosen_one = find_chosen(our_gravity)
            # print(chosen_one.get_id(), chosen_one.get_xpos(), chosen_one.get_ypos())
            self.chosen_one.set_as_chosen()
        
        
        """
        for n in normal.Normal.get_all_present_instances():
            for z in zombie.Zombie.get_all_present_instances():
                if n.is_near(z, 20) == True:
                    n.zombie_alert(z.get_xpos(), z.get_ypos())
        """

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
