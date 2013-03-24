import random
import agentsim
from person import Person
from moveenhanced import MoveEnhanced

# co-dependent imports
import normal
import defender

class Zombie(MoveEnhanced):
    my_target = None

    def __init__(self, **keywords):
        MoveEnhanced.__init__(self, **keywords)
        self.set_happiness(1)
        self._default_size = self.get_size()
        if agentsim.debug.get(2):
            print("Zombie", self._name)

    def get_author(self):
        return "Alexander Wong, Michelle Naylor"

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

    def compute_next_move(self):

        """
        These zombies move to their unique closest normal
        """
        
        if agentsim.debug.get(128):
            pass
        delta_x = 0
        delta_y = 0

        # Alex: Changed to min to increase speed and maneuverability
        self.set_size(self.get_min_size())

        all_n = normal.Normal.get_all_present_instances()
        if all_n:
            audition = []
            for i in all_n:
                n_distance = ((i.get_xpos() - self.get_xpos()) ** 2 + (i.get_ypos() - self.get_ypos()) ** 2) ** 0.5
                audition.append((i, n_distance))
            audition.sort(key=lambda targets: targets[1])
                        
            # Take the nearest normal that isn't already taken
            all_z = Zombie.get_all_present_instances()
            for i in all_z:
                if self == i:
                    continue
                for a in audition:
                    if i.my_target == a[0]:
                        audition.remove(a)
                        
            # Take the nearest normal that isn't already claimed
            if len(audition) > 0:
                target = audition[0][0]
                self.my_target = target

            # If all the normals are taken, take the nearest one
            else:
                self.my_target = None
                nearest = min(
                    # make pairs of (person, distance from self to person)
                    [ (n, self.distances_to(n)[0] ) for n in all_n ]
                    ,
                    # and sort by distance
                    key=(lambda x: x[1])
                    )
                (target, target_d) = nearest

            if agentsim.debug.get(128):
                try:
                    print("Zombie: ", self.get_name(), " Target: ", self.my_target.get_name())
                except:
                    print("Zombie No Target")
                    pass
                for i in all_n:
                    print("Normal: ", i.get_name(), " Distance to me: ", self.distances_to(i)[0])
                
            # move towards target
            (d, delta_x, delta_y, d_edge_edge) = self.distances_to(target)

            # if close to target, get bigger
            if d < 25:
                self.set_size(self.get_max_size())
        
        # See if zombie can move towards the target
        def_collision = False
        for i in Person.get_all_present_instances():
            if i == target:
                continue
            if (self.is_near_after_move(i, delta_x, delta_y, 1)):
                def_collision = True

        if def_collision:
            coordinates = (target.get_xpos(), target.get_ypos())
            if agentsim.debug.get(128):
                print("Rotation coordinates: ", coordinates)
            destination = (self.rotate_around_point(coordinates))
            print("Zombie destination: ", destination)
            return (destination[0] - self.get_xpos(), destination[1] - self.get_ypos())
        else:
            return (delta_x, delta_y)
