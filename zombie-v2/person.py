"""
Agent base class for simuulation

This class maintains information about a person in the simulation.

ID:

Every Person is assigned an ID on creation.  The ID is a unique integer >
0, and cannot be changed.

Accessors 
    p.get_id()


Name:

On construction, every Person is given a name.  The name need not be
unique, and cannot be changed.  If no name is supplied, a unique one is
generated from the object id.

Accessor
    p.get_name()


Position:

Every Person has a position (xpos, ypos) in the simulation room.  When the
Person is created, the initial position can be supplied.  After creation,
the position of the Person can only be changed via move_by method calls.

Accessors
    p.get_xpos()
    p.get_ypos()
    p.move_by(delta_x, delta_y)

Note: move_by is only a request to move, the actual motion made by the 
Person may be different!

The coordinate system for Person is the normal graphics plane.
That is, (0,0) is the top left, x and y increase to right and downward.  
This is the same as for the canvas in the Tk tool kit.
When the canvas is resized, then (0,0) should stay in the same place.

Hair Color:

Every Person has a hair color.  The hair color can be changed - for
example to indicate emotional state.

Accessors 
    p.get_haircolor()
    p.set_haircolor(color)

color can be a color name like 'red', 'green', 'blue', or it can be a RGB
color as encoded by rgb_to_color(r, g, b)

Happiness:

Every Person has a happiness value, a float, in the range [-1, 1].  This
is reflected in their facial expression.

Accessors
    p.get_happiness()
    p.set_happiness(level)

level is a value from -1 to 1, -1 indicating very unhappy, 0 being
neutral, and +1 being very happy.

Size:

Every person has a size, which can be changed, but is limited to at least
get_min_size() and at most get_max_size()

Accessors
    p.get_size()
    p.get_min_size()
    p.get_max_size()
    p.set_size(size)

Compute Next Move:

Every time step the agent is asked to compute its next move in the
simulation.

    (x_delta, y_delta) = p.compute_next_move()

returns a pair of x,y deltas that can be fed into move_by in order to move
to a new location in the simulation room

Distances To:

Much of the behaviour of an agent is determined by distances to other
agents, this can be computed with

    p.distances_to(q)

returns a 4-tuple (d, delta_x, delta_y, d_edge_edge) of
    d - the Euclidean distance between Person p and q
    delta_x - the difference q.get_xpos() - p.get_xpos()
    delta_y - the difference q.get_ypos() - p.get_ypos()
    d_edge_edge - the distance between the edges of the circumferences 
        of the objects, negative if they overlap

"""

from happyface import HappyFace
from shape import Shape
import agentsim

class Person():
    # Class variables:
    # id of the next object instance to be created
    _nextID = 1

    # dict of of all instances of Person, keyed by object id
    _instances = { }

    # Class methods
    # the @classmethod decorator causes the class that was used to invoke
    # the method to be passed as the first argument, just like a object
    # instance invocation.

    @classmethod
    def get_all_instances(cls):
        """
        return all instances of the class it was invoked with.  
        E.g.  Person.get_all_instances() returns all the Person objects
            or subclass of Person objects
        while
            Normal.get_all_instances() returns only the objects
            that are Normal or a subclass

        Also works if invoked on an object, getting all the instances
        of the class of the object

            p = Person()
            p.get_all_instances()
        """

        return [v for v in Person._instances.values() if isinstance(v, cls)]

    @classmethod
    def get_all_present_instances(cls):
        """
        return all instances of the class it was invoked with that 
        also satisfy the is_present test

        Also works if invoked on an object, getting all the instances
        of the class of the object

            p = Person()
            p.get_all_present_instances()
        """

        return [v for v in Person._instances.values() if 
            isinstance(v, cls) and v.is_present() ]

    @classmethod
    def get_instances_with_name(cls, name):
        """
        return all instances of the class it was invoked with and whose
        name exactly matches name.

        E.g.  Person.get_instances_name('fred') returns all the Person 
            objects or subclass of Person objects with name 'fred'
        while
            RandomPerson.get_instances_with_name'fred'() returns only 
            the objects that are RandomPerson or a subclass, and with
            matching name

        Also works if invoked on an object, getting all the instances
        of the class of the object

            p = Person(name='fred')
            p.get_instances_with_name('fred')

        """

        # better to write this as:
        # [ p for p in cls.get_all_instances if p.get_name() == name ]

        result = [ ]
        for p in Person._instances.values():
            if isinstance(p, cls) and p.get_name() == name:
                result.append(p)
        return result

    # Note: we could make the next two into @staticmethod, in which case
    # the class would not be passed through, but there might be cases
    # where the class is useful

    @classmethod
    def del_instance_with_id(cls, id):
        """
        Person.del_instance_with_id(id) removes the Person with the 
        given id from the inventory of instances.  It is hidden on 
        the canvas, but not immediately destroyed since there may be
        pending events on the object that have to be processed.

        Can we use sys.getrefcount() to tell us if it is safe to 
        "destroy" an object?
        """
        
        if id in Person._instances:
            Person._instances[id]._shape.hide()
            del(Person._instances[id])


    @classmethod
    def del_instance(cls, obj):
        """
        Percon.del_instance(p) is like del_instance_with_id but given
        the actual Person object p
        """

        # note the use of the cls variable that holds the name of 
        # the invoking class
        cls.del_instance_with_id(obj.get_id())


    def __init__(self, 
        name=None, 
        size=15,
        xpos=0,
        ypos=0,
        haircolor='blue',
        happiness=0.5,
        ):

        if agentsim.debug.get(2):
            print("Person init", self.__class__, self, 
                name, size, xpos, ypos, haircolor, happiness)

        self._id = Person._nextID
        Person._nextID += 1

        # set the name of the person from constructor parameters
        if name == None:
            self._name = "ID-" + str(self._id)
        else:
            self._name = name

        # size, haircolor, xpos, ypos, happiness are delegated to the
        # shape associated with the person
        # haircolor is mapped to color in the shape

        # create the shape associated with this instance
        # Arggh, the xpos = xpos form is confusing, but there is no way
        # around it without creating even more keyword names.  The xpos on 
        # the right is the value of the xpos argument to this function, 
        # which is begin provided to the xpos keyword of the HappyFace
        # constructor

        self._shape = HappyFace(
            xpos = xpos, ypos = ypos,
            size = size, color = haircolor,
            happiness = happiness,
            )

        # insert into collection of instances
        Person._instances[self._id] = self

    def arrive(self):
        """
        invoke this to have the person arrive at the simulation and become 
        visisble on the canvas
        """

        self._shape.draw()
        return self


    def leave(self):
        """
        invoke this to have the person leave the simulation and no longer
        be visisble on the canvas.  All the graphic components of the 
        associated Shape are destroyed.

        Note: does not delete the person, they still exist, and so if you
        want to avoid processing them, use is_present() to test their status
        They can rejoin the simulation later if they wish.
        """

        self._shape.erase()
        return self

    def is_present(self):
        """
        A person has a state, present or not present at the party.
        if they are not present, you might want to ignore them.

        is_present 
        returns 1 if the person is visible on the canvas
        returns 0 if the person is not visible on the canvas
        
        we do not have any explicit person state, the assumption is that
        if you are drawn, then you are present in the simulation
        """

        # NOTE: not good practice, should be asking shape if it is 
        # drawn or not, not inspect its state!  Yes I know about the
        # Law of Demeter
        if self._shape._gstate == Shape.DRAWN:
            return True
        else:
            return False

    def move_by(self, delta_x, delta_y):
        """
        """
        # move_by is delegated to the shape
        self._shape.move_by(delta_x, delta_y)
        return self

    def distances_to(self, other_person):
        """
        """
        delta_x = other_person.get_xpos() - self.get_xpos()
        delta_y = other_person.get_ypos() - self.get_ypos()
        d = (delta_x * delta_x + delta_y * delta_y) ** 0.5
        d_edge_edge = d - (self.get_size() + other_person.get_size())/2
        return  (d, delta_x, delta_y, d_edge_edge)

    # primary behaviour of the object
    def compute_next_move(self):
        return (0, 0)

    # accessors
    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    # all the remaining attributes are the responsibility of the shape
    # so the methods are delegate to corresponding methods in the shape
    def get_xpos(self):
        return self._shape.get_xpos()

    def get_ypos(self):
        return self._shape.get_ypos()

    def get_size(self):
        return self._shape.get_size()

    def get_min_size(self):
        return self._shape.get_min_size()

    def get_max_size(self):
        return self._shape.get_max_size()

    def set_size(self, size):
        return self._shape.set_size(size)

    def get_haircolor(self):
        return self._shape.get_color()

    def set_haircolor(self, haircolor):
        return self._shape.set_color(haircolor)

    def get_happiness(self):
        return self._shape.get_happiness()

    def set_happiness(self, happiness):
        return self._shape.set_happiness(happiness)
