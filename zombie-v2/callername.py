# http://docs.python.org/3.1/library/inspect.html?highlight=frame#inspect.currentframe

# Obtained from https://gist.github.com/techtonik/2151727
# See http://www.python.org/dev/peps/pep-3155/ for Python 3.3
# Public Domain, i.e. feel free to copy/paste
# Considered a hack in Python 2

import agentsim
import inspect
import re

def caller_name(level=1):
    """
    Get the name of a caller in the form of:
         module.class.method 
    that resulted in the call stack frame at the given level.
    
    level specifies the position in the call stack relative to the invoker of 
    caller_name.

    level 0 is the invoker of caller_name
    level 1 is the caller of the caller of caller_name (the normal case)

    An empty string is returned if level exceeds the call stack height.

    """

    stack = inspect.stack()
    start = 1 + level
    if len(stack) < start + 1:
      return ''

    parentframe = stack[start][0]    
    
    name = []
    module = inspect.getmodule(parentframe)

    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        name.append(module.__name__)

    # detect classname
    if 'self' in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(parentframe.f_locals['self'].__class__.__name__)

    codename = parentframe.f_code.co_name
    if codename != '<module>':  # top level usually
        name.append( codename ) # function or a method

    # it's important to free the frame to prevent dependency cycles
    del parentframe
    return ".".join(name)


def caller_name_match(rexp, level=1, abort=False, debug=True):
    """

    Used to enforce caller-callee relationships.  The caller of the
    function at level must match the regular expression in rexp.

    Don't forget the r"pattern" style of raw strings with no special
    \ interpretation

    abort - when True raises an exception, when False returns the
        result of the pattern match

    debug - when True causes a diagnostic message to be printed

    Example:
    def g():
        caller_name_match(r"__main__\.h$|\.foo.f$")
        # we get here only if called by function in main or function
        # f in module foo
    """
    called = caller_name(level)
    called_by = caller_name(level+1)
    if debug:
        print("At level", level, "method", called_by, "calls", called)

    match = re.search(rexp, called_by)
    
    if abort and match is None:
        raise Exception("Calling security violation.  '{}' was called by method '{}' with no match to '{}'".format(called, called_by, rexp))

    return match
