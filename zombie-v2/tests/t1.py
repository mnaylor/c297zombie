import callername
import re

def A():
    print(callername.caller_name_matches("."))

def B():
    print(callername.caller_name_matches("."))
    A()

def C():
    print(callername.caller_name_matches("."))
    B()
    A()

# C()

match = re.search(".", "__main__")
print(match)
match = re.search("X", "__main__")
print(match)
