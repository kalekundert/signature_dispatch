#!/usr/bin/env python3

"""
Execute the first function that matches the given arguments.

Use this module to decorate multiple functions of the same name.  When called, 
all of the decorated functions will be tested in order to see if they accept 
the given arguments.  The first one that does will be invoked.  A TypeError 
will be raised if none of the functions can accept the arguments.

Examples:

>>> import signature_dispatch
>>> @signature_dispatch
... def f(x):
...    return x
...
>>> @signature_dispatch
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
TypeError: can't dispatch the given arguments to any of the candidate functions:
arguments: 1, 2, 3
candidates:
(x): too many positional arguments
(x, y): too many positional arguments
"""

import sys, inspect
from functools import update_wrapper
from typeguard import check_type
from typing import Dict, Tuple

__version__ = '0.2.0'

def _auto_dispatch(f, stack_depth=1):
    caller = inspect.stack()[stack_depth]

    try:
        name = f.__name__
        locals = caller.frame.f_locals

        if name in locals:
            dispatcher = locals[name]
            if not hasattr(dispatcher, 'overload'):
                dispatcher = _make_dispatcher()
        else:
            dispatcher = _make_dispatcher()

        return dispatcher.overload(f)

    finally:
        del caller

def _make_dispatcher():
    # The dispatcher needs to be a real function (e.g. not a class with a 
    # `__call__()` method) so that it will be bound when used on methods.
    candidates = []

    def dispatcher(*args, **kwargs):
        assert candidates
        errors = []

        for f in candidates:
            sig = inspect.signature(f)
            try:
                bound_args = sig.bind(*args, **kwargs)
            except TypeError as err:
                errors.append(f"{sig}: {err}")
                continue

            try:
                _check_type_annotations(bound_args)
            except TypeError as err:
                errors.append(f"{sig}: {err}")
                continue

            break

        else:
            arg_reprs = map(repr, args)
            kwargs_reprs = (f'{k}={v!r}' for k, v in kwargs.items())
            arg_repr = ', '.join([*arg_reprs, *kwargs_reprs])
            raise TypeError("\n".join([
                "can't dispatch the given arguments to any of the candidate functions:",
                f"arguments: {arg_repr}",
                "candidates:",
                *errors,
            ]))

        return f(*args, **kwargs)

    def overload(f):
        if not candidates:
            update_wrapper(dispatcher, f)
        candidates.append(f)
        return dispatcher

    dispatcher.overload = overload
    return dispatcher

def _check_type_annotations(bound_args):
    for name, value in bound_args.arguments.items():
        param = bound_args.signature.parameters[name]
        if param.annotation is param.empty:
            continue

        if param.kind is param.VAR_POSITIONAL:
            expected_type = Tuple[param.annotation, ...]
        elif param.kind is param.VAR_KEYWORD:
            expected_type = Dict[str, param.annotation]
        else:
            expected_type = param.annotation

        check_type(name, value, expected_type)


# Hack to make the module directly usable as a decorator.  Only works for 
# python 3.5 or higher.  See this Stack Overflow post:
# https://stackoverflow.com/questions/1060796/callable-modules

class CallableModule(sys.modules[__name__].__class__):

    def __call__(self, f):
        return _auto_dispatch(f, stack_depth=2)

sys.modules[__name__].__class__ = CallableModule

