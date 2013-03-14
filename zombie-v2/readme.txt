2D Agent Simulation

NOTE: The ubuntu VM is missing the python3 tk module, which can be installed
with
    sudo apt-get install python3-tk

Version 2.4 - 2012-03-14
Fixed the converion of normals to zombies so that new zombie is the same size 
as the original normal.
Max size is changed to 60.

Version 2.3 - 2012-03-13
Fixed the resize processing that still had flipped y coordinate.
Fixed rgb_to_color documentation to match [0,1] range of color args.
Fixed missing guard in hair color change that would cause lookup of non-defined
    property.
Fixed problem in collision detector that would check against non-present 
    persons.
Added permission guards to move_by to prevent anything other than the main
    simulation from invoking it.
Added get_all_present_instances method to only return the instances that are
    present in the simulation room
When converting a Normal to a Zombie, the normal is now deleted.
Added a get_min_size, get_max_size operation to HappyFace and Person so that
    limit sizes

Version 2.2 - 2012-03-06
Cleaned up some of the framework code as a result of walkthrough in class.

Version 2.1 - 2012-02-29
Added Bouncer class (formerly Assassin) and a Paranoid that attempts to avoid
the bouncer.  This is in partygame-2.py.

Version 2.0 - 2012-02-29
This is the first Python 3 release of the simulation framework..

Use pydoc3 to see the documentation, as in 
    pydoc3 agentsim

Files:

package.sh - script for building files for actual assignment 

zombiegame.py - main program, run for example, with
    python3 zombiegame.py -normals 5 -defenders 1 -zombies 2

agentsim.py - main simulation framework module
bitflag.py - bit flag utility class

person.py - base class for the Person agent
shape.py - base class for the graphical Shape representing the Person
happyface.py - the HappyFace Shape we actually use

moveenhanced.py - base class for normal, zombie, and defender.  It enforces
the various rules of the game so that cheating is discouraged.

normal.py
zombie.py
defender.py
