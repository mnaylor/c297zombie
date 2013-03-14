import callername
import t2m

dbf = True
abf = True

def A():
    callername.caller_name_match("^t2m.fn$|^__main__\.B$", abort=abf, debug=dbf)

def B():
    callername.caller_name_match(".", abort=abf, debug=dbf)
    A()

def C():
    callername.caller_name_match(".", abort=abf, debug=dbf)
    B()
    A()

t2m.fn(A)
t2m.fn(B)
t2m.fn(C)
