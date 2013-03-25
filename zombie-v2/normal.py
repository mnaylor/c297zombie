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
# inititalize global homebase and lamb to none
homebase = None
lamb = None

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

    # find count of all zombies and normals in each corner
    # sort based on number of zombies
    count_list = [(corner, get_count_near_point(corner, all_z), 
                  get_count_near_point(corner, all_n))
                  for corner in corner_set]
    count_list.sort(key = lambda x:x[1])
    
    # initialize homebase to corner with least number of zombies
    homebase = count_list[0]
    
    # if there is a tie in number of zombies, choose corner with most normals
    for i in range(3):
        if homebase[1] == count_list[i + 1][1]:
            if count_list[i][2] < count_list[i+1][2]:
                homebase = count_list[i+1]

    if agentsim.debug.get(32):
        print("homebase is {} with {} zombies and {} normals".
              format(homebase[0], homebase[1], homebase[2]))

    return homebase[0]

def invading_zombie(home):
    """
    checks to see if a zombie is near homebase
    if yes, returns the nearest zombie
    """
    # find all zombies
    all_z = zombie.Zombie.get_all_present_instances()

    # find nearest zombie to homebase
    if all_z:
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
    global lamb
    all_n = Normal.get_all_present_instances()
                
    # sacrificial lamb is the normal closest to the zombie
    lamb_dist = min(
        [(n, invader.distances_to(n)[0]) for n in all_n]
        , key = (lambda x:x[1]))
                
    (lamb, dist) = lamb_dist

    # make lamb scared and red
    lamb.set_happiness(-1)
    lamb.set_haircolor("red")    

    if agentsim.debug.get(32):
        print("normal {} is the sacrificial lamb".format(lamb.get_name()))

    return lamb

class Normal(MoveEnhanced):

    def __init__(self, **keywords):

        MoveEnhanced.__init__(self, **keywords)

        # this records the information from the most recent
        # zombie alert move.  When compute_next_move() is called, 
        # this information can be processed.

        self._zombie_alert_args = None
        
        self._at_home = False
        self._initial = True

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
        # move towards home base
        else:
            delta_x = homebase[0] - self.get_xpos()
            delta_y = homebase[1] - self.get_ypos()

        # check for collissions
        obstacle = self.collision_check(delta_x, delta_y)

        if obstacle:
            destination = self.rotate_around_point((
                    obstacle.get_xpos(), obstacle.get_ypos()))
            delta_x = destination[0] - self.get_xpos()
            delta_y = destination[1] - self.get_xpos()

        # if near homebase, set self._at_home to true
        if (self._at_home == False and 
            distance_to_point(self, homebase) < normal_near):
            self._at_home = True
            self.set_happiness(0.5)
            if agentsim.debug.get(32):
                print("normal {} is at home".format( self.get_name()))

        return (delta_x, delta_y)

    def collision_check(self, delta_x, delta_y):
        # find potential collisions
        for p in Person.get_all_present_instances():
            if p == self: break
            (d, dx, dy, d_e_e) = self.distances_to(p)
            dx = dx - delta_x
            dy = dy - delta_y
            d = (dx*dx + dy*dy) ** 0.5  - (self.get_size() 
                + p.get_size()) / 2
            
            # if distance between self and person < move_limit, return
            # person that is in the way
            if abs(d) < self.get_move_limit():
                if agentsim.debug.get(32):
                    print("collision between {} and {} at distance {}".format(
                            self.get_name(), p.get_name(), d))
                return p

    def rotate_around_point(self, point):
        # Use pythagorean theorm to determine move location
        # Ideally, 30-60-90, right angle is 
        # "C: Move To Location > B: Current Location > A: Chosen One Location"
        # ABC = 90, CAB = 60, BCA = 30
        rotator = (point[0], point[1])
        origin = (self.get_xpos(), self.get_ypos())
        angle = 1/(3**0.5)
        turning = ((origin[0] + angle*(rotator[1] - origin[1])), (origin[1] 
                   + angle*(origin[0] - rotator[0])))
        return turning

    def lamb_move(self, homebase, invader):
        """
        sacrificial lamb will move away from homebase (for now)
        """
        x = 0
        y = 0

        # if zombie alert, factor into run away from homebase
        if self._zombie_alert_args is not None:
            (x, y) = self._zombie_alert_args
        # clear alert
        self._zombie_alert_args = None 

        # move away from homebase & zombie
        delta_x = self.get_xpos() - (homebase[0] + x)
        delta_y = self.get_ypos() - (homebase[1] + y)

        # check for collissions
        obstacle = self.collision_check(delta_x, delta_y)
        
        if obstacle:
            destination = self.rotate_around_point((
                    obstacle.get_xpos(), obstacle.get_ypos()))
            delta_x = destination[0] - self.get_xpos()
            delta_y = destination[1] - self.get_xpos()

        return (delta_x, delta_y)         

    def compute_next_move(self):
        # if no homebase, set homebase
        global homebase
        global lamb
        delta_x = 0
        delta_y = 0

        if self._initial == True:
            for p in Person.get_all_present_instances():
                # if overlapping another person, move to another
                # random spot
                if self.is_near(p) == True:
                    if agentsim.debug.get(32):
                        print("{} and {} are overlapping".format(
                                self.get_name(), p.get_name()))
                        self.set_size(self.get_min_size())
            self._initial = False

        # find all zombies
        all_z = zombie.Zombie.get_all_present_instances()

        if homebase == None:
            homebase = set_homebase()

        # if zombie is near homebase, send sacrificial lamb
        invading_z = invading_zombie(homebase)
        if invading_z:
            lamb = sacrificial_lamb(invading_z)
            
        # sucker, you are bait
        if lamb and self.get_id() == lamb.get_id():
            (delta_x, delta_y) = self.lamb_move(homebase, invading_z)

        # default, move towards homebase
        else:
            (delta_x, delta_y) = self.move_to_homebase()

        # and change happiness
        delta_h = 0.5 * (0.5 - random.random())
        self.set_happiness(delta_h + self.get_happiness())

        return (delta_x, delta_y)

    def zombie_alert(self, x_dest, y_dest):
        # ignore any request not from a defender!
        # Only the chosen one will get a zombie alert ping
        caller_name = callername.caller_name()

        if not re.search(r"\.Defender\.", caller_name):
            raise Exception("zombie alert on {} called by non-Defender {}"
                            .format(self.get_name(), caller_name))

        if agentsim.debug.get(32):
            print("zombie_alert to ({}, {})".format( self.get_name(), x_dest, y_dest))

        # remember where the alert told us to go so that we can use this
        # information when we compute the next move
        self._zombie_alert_args = (x_dest, y_dest)
        # Make self tiny! This is necessary for the chosen one code, and this is the only
        # way to communicate without adding a new function/field which will break with 
        # other modules
        # make chosen one really happy, he has been chosen!
        self.set_size(self.get_min_size())
        self.set_happiness(1)
