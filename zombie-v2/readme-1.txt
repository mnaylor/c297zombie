CMPUT 297 Assignment 2 - The Zombie Game
Version 2.2
2013-03-13

In this assignment you will use our party game simulation framework to simulate
the zombie plague.  The initial conditions for the simulation will be arbitrary
(small, total < 50) numbers of normals, zombies, and defenders.  

To add a bit of friendly competition, one measure of success for your simulation
will be how well your defenders, normals, and zombies manage to do something 
interesting.

Thus we need to be able to mix and match your people with those of other
students.  So you need to ensure that your new classes of Normal, Zombie, and
Defender are self-contained.  

Since we are mixing classes from other students, we need to be able to
identify the author of a class, so each object must have a 
    get_author()
method which returns a string that contains the names of the authors
of the class, separated by commas in the case of multiple creators.  

For example, if p is a zombie, then
    p.get_author()
might return
    "Logan Gilmour, Jim Hoover, Martha White"

In addition, if you have a special relationship between normals and defenders,
or between your zombies, then your classes will need to be able to detect when
they are communicating with a class implemented by someone else.  You can use
the get_author() method to determine if you are talking to a class that you
have written and so can exploit special features.

* MoveEnhanced Base Class *

To make the simulation realistic, we need to limit the speed at which the
people can move, add a special feature allowing zombie teleporting, and prevent
persons from occupying the same space.  Thus we created a new subclass of
Person, called MoveEnhanced that adds this behavior to Person.  MoveEnhanced
then forms the base class from which we develop Normal, Zombie, and Defender

* Limited move per step *

MoveEnhanced class has a new attribute called _move_limit, which sets the 
maximum amount that a person can move per call of move_by.  Move limit is 
set on creation, and you have no control over it.  Thus it has just the
accessor 
    get_move_limit() 

A call to move_by(delta_x, delta_y) moves the person by a distance 
    delta = (delta_x * delta_x + delta_y * delta_y) ** 0.5

The constraint for MoveEnhanced is that delta must obey 
    delta <= _move_limit
If not, then delta_x and delta_y will be proportionately scaled to satisfy the 
move limit.  That is, if delta > _move_limit then scale by
    delta_x_actual = delta_x * max/delta
    delta_y_actual = delta_y * max/delta

The total amount of moving for an object via move_by per simulation step must
be less than the move limit.  This is enforced because you never actually make
a call to move_by inside your class.  All movement (except for teleportation)
is created by the compute_next_move() function which then returns a position
change to the simulator.

* Zombie teleportation by defenders *

MoveEnhanced objects also have a special teleport method
    p.teleport(target, x_dest, y_dest) 
that when invoked by an MoveEnhanced object with teleport rights
and within teleporting distance of MoveEnhanced object p causes target to
instantly move to the location (x_dest, y_dest).  

The teleporting distance for object p can be accessed by
    p.get_teleporting_threshold()

At each simulation step, all defenders are processed, then all normals, and
finally all zombies.  Thus on each simulation step, the compute_next_move()
invocation for a zombie always occurs after any teleport operations.

* Conversion of normals to zombies *

When a zombie z gets within z.get_touching_threshold() of a normal, the
simulation causes an zombie conversion.  This causes the Normal to die (i.e
leave the simulation) and uses the energy of the normals' death to create a new
Zombie that is located in the place of the now deceased Normal.  

NOTE:  The reason we do the leave and arrive with a replacement is because you
cannot easily transform an instance of one class into another.  One could argue
that what is actually going on here is a case of role changing.  Using 
inheritance to model roles is tricky.

* No sharing of physical space *

Finally, persons are not permitted to move or teleport to the place occupied by
an existing person.  If you attempt to do so, then the operation will fail and
no move is done.

* TASKS *

You will need to construct 3 kinds of subclasses of MoveEnhanced, whose basic
behavior is as follows:

Normal -  normals move around doing their daily activities.  Yhey might want to
try to avoid Zombie instances.  Each Normal has a 

    zombie_alert(x_dest, y_dest) 

method, that can be invoked by a Defender to give a move hint to a Normal For
example, that might causes the Normal to go as fast as possible toward point 
(x_dest, y_dest), while still trying to avoid Zombies.  This way, Defenders
have a limited ability to tell Normals what to do.  NOTE: zombie_alert does not
actually cause any movement, it information is simply saved for use by a
subsequent comput_next_move() invocation on the normal.

Zombies - zombies move around.  If a Zombie comes within touching distance of
a Normal it cause the normal to be replaced by a zombie.

Defenders - the job of defenders is to keep the Zombies away from the Normals.
If a Defender can get within touching distance of a Zombie, then the Defender
can invoke the zombie's teleport method and send the Zombie to any point in the
party room.  Note that Defenders cannot be turned into Zombies.

Inter Person Collaboration:  you are allowed to add all kinds of collaborative
behaviour to your classes, such as electing a leader which then gives orders to
the other defenders and normals.  Zombies could talk to each other and
coordinate attacks.  You just must be sure that your classes will continue to
work with the classes created by others, possibly by disabling fancy features
when you encounter classes that are not yours.

* ALLOWABLE OPERATIONS in compute_next_move() *
only get operations, and teleport

* EVALUATION MECHANISM *

You have no control over the starting configuration
There could be no members of a given class present
Only one type of each

Code quality

The object of this exercise is to produce interesting behaviour


* WHAT TO SUBMIT *

The only files you will be submitting are normal.py, defender.py, and 
zombie.py, each of which is implementing the corresponding class of
Normal, Defender, and Zombie.  So you must be careful not to have any
hidden behavior in your zombie game main routine.  You will not be allowed
any other modules, and should not alter any of the supporting modules or
programs except to fix bugs.  There will always be a current reference set
of support modules for you to test your people against.

You should submit a single zip file, called zombie.zip that contains a single
directory, zombiegame, that has just the classes: 
    normal.py, defender.py, zombie.py.


