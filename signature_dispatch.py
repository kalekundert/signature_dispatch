#!/usr/bin/env python3

"""
Execute the first function that matches the given arguments.

Use this object to decorate multiple functions.  When called, all of the 
decorated functions will be tested in order to see if they accept the given 
arguments.  The first one that does will be invoked.  A TypeError will be 
raised if none of the functions can accept the arguments.

Each decorated function will be replaced by the same callable.  To avoid 
confusion, then, it's best to use the same name for each function.  The 
docstring of the ultimate callable will be taken from the final decorated 
function.

Examples:

>>> import signature_dispatch
>>> dispatch = signature_dispatch()
>>> @dispatch
... def f(x):
...    return x
...
>>> 
>>> @dispatch
... def f(x, y):
...    return x, y
...
>>> f(1)
1
>>> f(1, 2)
(1, 2)
>>> f(1, 2, 3)
Traceback (most recent call last):
    ...
TypeError: f() takes 2 positional arguments but 3 were given
"""

import sys, inspect
from functools import update_wrapper

__version__ = '0.0.0'

class Decorator:
    __doc__ = __doc__

    def __init__(self):
        self.dispatcher = Dispatcher()

    def __call__(self, f):
        self.dispatcher += f
        return update_wrapper(self.dispatcher, f)

class Dispatcher:

    def __init__(self):
        self.candidates = []

    def __iadd__(self, f):
        self.candidates.append(f)
        return self

    def __call__(self, *args, **kwargs):
        assert self.candidates

        for f in self.candidates:
            sig = inspect.signature(f)
            try:
                sig.bind(*args, **kwargs)
                break
            except TypeError:
                continue

        return f(*args, **kwargs)




# Hack to make the module directly usable as a decorator.  Only works for 
# python 3.5 or higher.  See this Stack Overflow post:
# https://stackoverflow.com/questions/1060796/callable-modules

class CallableModule(sys.modules[__name__].__class__):

    def __call__(self):
        return Decorator()

sys.modules[__name__].__class__ = CallableModule
