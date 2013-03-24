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

"""
These defenders are taking advantage of a bug with size changing.
It will choose three available defenders to guard a 'chosen' normal
by engulfing the normal into the defender's circle.

NOTE: Chosen defenders will be a ratio of 1:3 of all defenders, with a 
minimum of 1 chosen defender at all times.
ie) 1 defender -> 1 chosen defender, 0 normal defenders
6 defenders -> 2 chosen defenders, 4 normal defenders
5 defenders -> 1 chosen defender, 4 normal defenders
"""

def fix_coordinates(coordinates):
    """
    This function attempts to reduce the error checking for
    the move enhanced functions by reducing the coordinates to +- 10
    """
    fix_coords = [0,0]
    if coordinates[0] < -10:
        fix_coords[0] = -10
    elif coordinates[0] > 10:
        fix_coords[0] = 10
    else:
        fix_coords[0] = coordinates[0]
    if coordinates[1] < -10:
        fix_coords[1] = -10
    elif coordinates[1] > 10:
        fix_coords[1] = 10
    else:
        fix_coords[1] = coordinates[1]
    direct = (fix_coords[0], fix_coords[1])
    return direct

def find_chosen(gravity):
    """
    This function takes a coordinate and finds the normal closest to it
    """
    min_grav = float("inf")
    chosen_one = None
    all_normals = normal.Normal.get_all_present_instances()
    if len(all_normals) > 0:
        for n in all_normals:
            location = (n.get_xpos(), n.get_ypos())
            priority = ((gravity[0] - location[0]) ** 2 + (gravity[1] - location[1]) ** 2) ** 0.5
            if priority < min_grav:
                min_grav = priority
                chosen_one = n
        return chosen_one
    else:
        return None

def get_chosen_defenders():
    all_defenders = Defender.get_all_instances()
    chosen_defenders = []
    for i in all_defenders:
        if i.chosen_defender == True:
            chosen_defenders.append(i)
    return chosen_defenders
    
class Defender(MoveEnhanced):
    """
    Goes around attempting to prevent zombies from reaching normals
    """
    chosen_one = None
    chosen_defender = None

    def __init__(self, **keywords):
        MoveEnhanced.__init__(self, **keywords)

        self._default_size = self.get_size()

        if agentsim.debug.get(2):
            print("Defender", self._name)

    def get_author(self):
        return "Alexander Wong, Michelle Naylor"

    def get_defender_gravity(self):
        """
        This will get the center of gravity for all present defenders
        """
        all_defenders = self.get_all_present_instances()
        # Find the average coordinates of all the defenders in the field
        count_defender = 0
        x_holder = 0
        y_holder = 0
        for i in all_defenders:
            if agentsim.debug.get(64):
                print("Defender: ", i.get_id(), i.get_xpos(), i.get_ypos())
            x_holder += i.get_xpos()
            y_holder += i.get_ypos()
            count_defender += 1
        x_holder = x_holder/count_defender
        y_holder = y_holder/count_defender
        gravity = (x_holder, y_holder)
        if agentsim.debug.get(64):
            print("All Defenders Gravity: ", gravity)
        return gravity
    
    def get_chosen_gravity(self):
        """
        This will get the center of gravity for chosen defenders
        """
        all_defenders = self.get_all_present_instances()
        # Find the average coordinates of the chosen defenders in the field
        count_defender = 0
        x_holder = 0
        y_holder = 0
        for i in all_defenders:
            if ((i.chosen_defender == False) or i.chosen_defender == None):
                continue
            if agentsim.debug.get(64):
                print("Defender: ", i.get_id(), i.get_xpos(), i.get_ypos())
            x_holder += i.get_xpos()
            y_holder += i.get_ypos()
            count_defender += 1
        x_holder = x_holder/count_defender
        y_holder = y_holder/count_defender
        gravity = (x_holder, y_holder)
        if agentsim.debug.get(64):
            print("All Chosen Gravity: ", gravity)
        return gravity

    def create_chosen_defenders(self, gravity):
        """
        This function sets the chosen defender values for the chosen
        defenders closest to the gravity equal to True, while the
        rest of the defenders are equal to zero

        This function should only modify values once per game
        Once chosen defenders are set, they are set for the duration 
        """
        all_defenders = self.get_all_present_instances()
        audition = []
        for i in all_defenders:
            gravity_dist = ((i.get_xpos() - gravity[0])**2 + (i.get_ypos() 
                            - gravity[1])**2) ** 0.5
            audition.append((i, gravity_dist))
        sorted(audition, key=lambda defender: defender[1]) 
        # Sort by distance, lowest to highest
        # and make them the sacred chosen guardians
        
        for i in audition:
            # Change this number to adjust number of chosen defenders
            # Will be a ratio 1/3rd of all defenders
            num_chosen_defenders = len(Defender.get_all_present_instances())//3
            if num_chosen_defenders <= 0:
                num_chosen_defenders == 1
                i[0].chosen_defender = True
                break
            if len(get_chosen_defenders()) == num_chosen_defenders:
                break
            else:
                # i[0].set_size(i[0].get_min_size())
                i[0].chosen_defender = True
        return

    def rotate_around_chosen(self):
        # Use pythagorean theorm to determine move location
        # Ideally, 30-60-90, right angle is 
        # "C: Move To Location > B: Current Location > A: Chosen One Location"
        # ABC = 90, CAB = 60, BCA = 30
        rotator = (self.chosen_one.get_xpos(), self.chosen_one.get_ypos())
        origin = (self.get_xpos(), self.get_ypos())
        angle = 1/(3**0.5)
        turning = ((origin[0] + angle*(rotator[1] - origin[1])), (origin[1] 
                   + angle*(origin[0] - rotator[0])))
        return turning        
    
    def compute_next_move(self):
        delta_x = 0
        delta_y = 0

        # revert back to original size
        # /max size if you are a chosen defender
        self.set_size(self._default_size)

        # Find the gravity of the defenders
        def_gravity = self.get_defender_gravity()
        # Assign at most 1/3rd of all defenders to be the chosen defenders
        # Take the defenders closest to the gravity well
        if len(get_chosen_defenders()) == 0:
            self.create_chosen_defenders(def_gravity)
        # If we have no chosen one find the new chosen one
        # Find the gravity of the chosen defenders
        cho_gravity = self.get_chosen_gravity()
        if (self.chosen_one == None):
            if (agentsim.debug.get(64)):
                print("Finding new chosen due to chosen_one == None")
            self.chosen_one = find_chosen(cho_gravity)
            if (agentsim.debug.get(64)):
                if self.chosen_one == None:
                    print("Chosen One cannot be found. All normals dead?")
                else:
                    print("Chosen One: ", self.chosen_one.get_id(), 
                          self.chosen_one.get_xpos(), self.chosen_one.get_ypos())
        # If our chosen one no longer exists, find the new chosen one
        if (self.chosen_one not in normal.Normal.get_all_present_instances()):
            if (agentsim.debug.get(64)):
                print("Finding new chosen due to chosen_one not in normal instances")
            self.chosen_one = find_chosen(cho_gravity)
            if (agentsim.debug.get(64)):
                if self.chosen_one == None:
                    print("Chosen One cannot be found. All normals dead?")
                else:
                    print("Chosen One: ", self.chosen_one.get_id(), 
                          self.chosen_one.get_xpos(), self.chosen_one.get_ypos())
        
        destination = (cho_gravity[0] - self.get_xpos(), 
                       cho_gravity[1] - self.get_ypos())
        
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
            if n == self.chosen_one:
                self.chosen_one.zombie_alert(cho_gravity[0], cho_gravity[1])
                continue
            else:
                for z in zombie.Zombie.get_all_present_instances():
                    if n.is_near(z, 20) == True:
                        n.zombie_alert(z.get_xpos(), z.get_ypos())
        
        # If chosen protector, protect the chosen
        if (self.chosen_defender == True) and (self.chosen_one != None):
            # See if you can move towards the chosen one
            def_collision = False
            tentative = (self.chosen_one.get_xpos() - self.get_xpos(), 
                         self.chosen_one.get_ypos() - self.get_ypos())
            tentative = fix_coordinates(tentative)
            for i in Person.get_all_present_instances():
                if i == self.chosen_one:
                    continue
                if (self.is_near_after_move(i, tentative[0], tentative[1], 1)):
                    # Cannot move towards chosen one, 
                    def_collision = True
            if (def_collision):
                if agentsim.debug.get(64):
                    print("MoveEnhanced.move_by", self.get_name(), 
                          "would collide with", i.get_name(), 
                          tentative[0], tentative[1])
                destination = self.rotate_around_chosen()
                self.set_size(self.get_max_size())
                return (destination[0] - self.get_xpos(), destination[1] - self.get_ypos()) 
            else:
                self.set_size(self.get_min_size())
                for p in Person.get_all_present_instances():
                    if self.is_near_after_move(p, tentative[0], tentative[1]):
                        self.set_size(self.get_max_size())
                return tentative
                if self.is_near(self.chosen_one, 5):
                    self._default_size = self.get_max_size()
                #return (destination[0] - self.get_xpos(), destination[1] - self.get_ypos())   
            return tentative

        # Else go kill the nearest zombie
        else:
            # if close to zombie, get bigger to swallow zombie
            if all_z and d < 25:
                self.set_size(self.get_max_size())
            return (delta_x, delta_y)
