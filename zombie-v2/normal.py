import random
import agentsim
from person import Person
from moveenhanced import MoveEnhanced
import callername
import re

# co-dependent imports
import zombie
import defender

# used to calculate distance to homebase
zombie_near = 250
normal_near = 100
# inititalize global homebase to none
homebase = None


def distance_to_point(person, point):
    """
    returns the distance between a person, and a (x, y) point in the playground
    """
    delta_x = point[0] - person.get_xpos()
    delta_y = point[1] - person.get_ypos()
    d = (delta_x * delta_x + delta_y * delta_y) ** 0.5

    return d

def get_count_near_point(point, group):
    """
    returns the number of person-class members near a (x, y) point
    """
    # intialize count to 0
    count = 0
    for person in group:
        if distance_to_point(person, point) < zombie_near:
            count = count + 1

    if agentsim.debug.get(32):
        print("there are {} persons near point {}".format(count, point))

    return count

def set_homebase():
    """
    returns the corner with the lowest number of zombies
    """
    # find all zombies
    all_z = zombie.Zombie.get_all_present_instances()
    all_n = Normal.get_all_present_instances()

    # get corner coordinates
    (x_min, y_min, x_max, y_max) = agentsim.gui.get_canvas_coords()
    corner_set = ((0,0), (x_max, y_min), (x_min, y_max), (x_max, y_max))

    # set homebase to be the corner with the least # of zombies
    homebase = min(
        [(corner, get_count_near_point(corner, all_z), get_count_near_point(corner, all_n))
         for corner in corner_set],
         key = (lambda x:x[1])
        )

    if agentsim.debug.get(32):
        print("homebase is {} with {} zombies".format(homebase[0], homebase[1]))

    return homebase[0]

def invading_zombie(home):
    """
    checks to see if a zombie is near homebase
    if yes, returns the nearest zombie
    """
    # find all zombies
    all_z = zombie.Zombie.get_all_present_instances()

    # find nearest zombie to homebase
    z_near_home = min(
        [ (z, distance_to_point(z, homebase)) for z in all_z ],
        key = (lambda x: x[1]) )

    (invading_z, dist_z) = z_near_home
           
    # if zombie is within homebase threshold
    if dist_z < zombie_near:
        return invading_z

def sacrificial_lamb(invader):
    """
    selects sacrificial lamb to be used as zombie bait
    """
    all_n = Normal.get_all_present_instances()
                
    # sacrificial lamb is the normal closest to the zombie
    lamb_dist = min(
        [ (n, invader.distances_to(n)[0]) for n in all_n ]
        , key = (lambda x:x[1]))
                
    (lamb, dist) = lamb_dist
        
    return lamb

class Normal(MoveEnhanced):

    def __init__(self, **keywords):

        MoveEnhanced.__init__(self, **keywords)

        # this records the information from the most recent
        # zombie alert move.  When compute_next_move() is called, 
        # this information can be processed.

        self._zombie_alert_args = None

        self._at_home = False

        if agentsim.debug.get(2):
            print("Normal", self._name)

        self.set_happiness(1 - 2 * random.random())
        self.set_size(random.uniform(self.get_min_size(), self.get_max_size()))

    def get_author(self):
        return "Alexander Wong, Michelle Naylor"
        
    def move_to_homebase(self):
        # if we have a pending zombie alert, act on that first
        if self._zombie_alert_args is not None:
            (x, y) = self._zombie_alert_args
            delta_x = x - self.get_xpos()
            delta_y = y - self.get_ypos()
            # clear the alert
            self._zombie_alert_args = None 
        # move towards zombie base
        else:
            delta_x = homebase[0] - self.get_xpos()
            delta_y = homebase[1] - self.get_ypos()

        # if near homebase, set self._at_home to true
        if distance_to_point(self, homebase) < normal_near:
            self._at_home = True
            if agentsim.debug.get(32):
                print("normal {} is at home".format( self.get_name()))

        return (delta_x, delta_y)

    def lamb_move(self, homebase, invader):
        """
        sacrificial lamb will move away from homebase (for now)
        """
        delta_x = self.get_xpos() - homebase[0]
        delta_y = self.get_ypos() - homebase[1]

        return (delta_x, delta_y)
            

    def compute_next_move(self):
        # if no homebase, set homebase
        global homebase
        delta_x = 0
        delta_y = 0
        lamb = None

        # find all zombies
        all_z = zombie.Zombie.get_all_present_instances()

        if homebase == None:
            homebase = set_homebase()
             
        # move towards homebase if not yet near homebase
        if self._at_home == False:
            (delta_x, delta_y) = self.move_to_homebase()
            return (delta_x, delta_y)

        # if zombie is near homebase, send sacrificial lamb
        invading_z = invading_zombie(homebase)
        if invading_z and not lamb:
            lamb = sacrificial_lamb(invading_z)
            
            # sucker, you are bait
            if self.get_id() == lamb.get_id():
                (delta_x, delta_y) = self.lamb_move(homebase, invading_z)
                if agentsim.debug.get(32):
                    print("normal {} is the sacrificial lamb".format( self.get_name()))

        # default, move towards homebase
        else:
            (delta_x, delta_y) = self.move_to_homebase()

        # and change happiness
        delta_h = 0.5 * (0.5 - random.random())
        self.set_happiness(delta_h + self.get_happiness())

        return (delta_x, delta_y)

    def zombie_alert(self, x_dest, y_dest):
        # ignore any request not from a defender!
        caller_name = callername.caller_name()

        if not re.search(r"\.Defender\.", caller_name):
            raise Exception("zombie alert on {} called by non-Defender {}"
                            .format(self.get_name(), caller_name))

        if agentsim.debug.get(32):
            print("zombie_alert to ({}, {})".format( self.get_name(), x_dest, y_dest))

        # remember where the alert told us to go so that we can use this
        # information when we compute the next move
        self._zombie_alert_args = (x_dest, y_dest)