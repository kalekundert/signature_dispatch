******************
Signature Dispatch
******************

``signature_dispatch`` is a simple python library for overloading functions 
based on their call signature and type annotations.

.. image:: https://img.shields.io/pypi/v/signature_dispatch.svg
   :alt: Last release
   :target: https://pypi.python.org/pypi/signature_dispatch

.. image:: https://img.shields.io/pypi/pyversions/signature_dispatch.svg
   :alt: Python version
   :target: https://pypi.python.org/pypi/signature_dispatch

.. image::
   https://img.shields.io/github/workflow/status/kalekundert/signature_dispatch/Test%20and%20release/master
   :alt: Test status
   :target: https://github.com/kalekundert/signature_dispatch/actions

.. image:: https://img.shields.io/coveralls/kalekundert/signature_dispatch.svg
   :alt: Test coverage
   :target: https://coveralls.io/github/kalekundert/signature_dispatch?branch=master

.. image:: https://img.shields.io/github/last-commit/kalekundert/signature_dispatch?logo=github
   :alt: GitHub last commit
   :target: https://github.com/kalekundert/signature_dispatch

Installation
============
Install from PyPI::

  $ pip install signature_dispatch

Version numbers follow `semantic versioning`__.

__ https://semver.org/

Usage
=====
Use the module itself to decorate multiple functions (or methods) that all have 
the same name::

  >>> import signature_dispatch
  >>> @signature_dispatch
  ... def f(x):
  ...    return x
  ...
  >>> @signature_dispatch
  ... def f(x, y):
  ...    return x, y
  ...

When called, all of the decorated functions will be tested in order to see if 
they match the given arguments.  The first one that does will be invoked::

  >>> f(1)
  1
  >>> f(1, 2)
  (1, 2)

A ``TypeError`` will be raised if no matches are found::

  >>> f(1, 2, 3)
  Traceback (most recent call last):
      ...
  TypeError: can't dispatch the given arguments to any of the candidate functions:
  arguments: 1, 2, 3
  candidates:
  (x): too many positional arguments
  (x, y): too many positional arguments

Type annotations are taken into account when choosing which function to 
invoke::

  >>> from typing import List
  >>> @signature_dispatch
  ... def g(x: int):
  ...    return 'int', x
  ...
  >>> @signature_dispatch
  ... def g(x: List[int]):
  ...    return 'list', x
  ...

::

  >>> g(1)
  ('int', 1)
  >>> g([1, 2])
  ('list', [1, 2])
  >>> g('a')
  Traceback (most recent call last):
      ...
  TypeError: can't dispatch the given arguments to any of the candidate functions:
  arguments: 'a'
  candidates:
  (x: int): type of x must be int; got str instead
  (x: List[int]): type of x must be a list; got str instead
  >>> g(['a'])
  Traceback (most recent call last):
      ...
  TypeError: can't dispatch the given arguments to any of the candidate functions:
  arguments: ['a']
  candidates:
  (x: int): type of x must be int; got list instead
  (x: List[int]): type of x[0] must be int; got str instead

Details
=======
- When using the module directly as a decorator, every implementation of the 
  function must have the same name and be defined in the same local scope.  If 
  this is not possible (e.g. the implementations are in different modules), 
  every function decorated with ``@signature_dispatch`` provides an 
  ``overload()`` method that can be used to add implementations defined 
  elsewhere::

    >>> @signature_dispatch
    ... def h(x):
    ...    return x
    ...
    >>> @h.overload
    ... def _(x, y):
    ...    return x, y
    ...
    >>> h(1)
    1
    >>> h(1, 2)
    (1, 2)

- The docstring will be taken from the first decorated function.  All other 
  docstrings will be ignored.

- It's possible to use ``@signature_dispatch`` with class/static methods, but 
  doing so is a bit of a special case.  Basically, the class/static method must 
  be applied after all of the overloaded implementations have been defined::

    >>> class C:
    ...
    ...     @signature_dispatch
    ...     def m(cls, x):
    ...         return cls, x
    ...
    ...     @signature_dispatch
    ...     def m(cls, x, y):
    ...         return cls, x, y
    ...
    ...     m = classmethod(m)
    ...
    >>> obj = C()
    >>> obj.m(1)
    (<class '__main__.C'>, 1)
    >>> obj.m(1, 2)
    (<class '__main__.C'>, 1, 2)

  Let me know if you find this too annoying.  It would probably be possible to 
  special-case class/static methods so that you could just apply both 
  decorators to all the same functions, but that could be complicated and this 
  work-around seems fine for now.

Applications
============
Writing decorators that can *optionally* be given arguments is `tricky to get 
right`__, but ``signature_dispatch`` makes it easy.  For example, here is a 
decorator that prints a message to the terminal every time a function is called 
and optionally accepts an extra message to print::

  >>> import signature_dispatch, functools
  >>> from typing import Optional

  >>> @signature_dispatch
  ... def log(msg: Optional[str]=None):
  ...     def decorator(f):
  ...         @functools.wraps(f)
  ...         def wrapper(*args, **kwargs):
  ...             print("Calling:", f.__name__)
  ...             if msg: print(msg)
  ...             return f(*args, **kwargs)
  ...         return wrapper
  ...     return decorator
  ...
  >>> @signature_dispatch
  ... def log(f):
  ...     return log()(f)

__ https://stackoverflow.com/questions/653368/how-to-create-a-python-decorator-that-can-be-used-either-with-or-without-paramet

Using ``@log`` without an argument::

  >>> @log
  ... def foo():
  ...     pass
  >>> foo()
  Calling: foo

Using ``@log`` with an argument::

  >>> @log("Hello world!")
  ... def bar():
  ...     pass
  >>> bar()
  Calling: bar
  Hello world!

Alternatives
============
The dispatching_ library does almost the same thing as this one, with a few 
small differences:

- More boilerplate.
- Subscripted generic types (e.g. ``List[int]``) are not supported.
- Annotations can be arbitrary functions.

.. _dispatching: https://github.com/Lucretiel/Dispatch

PEP 3124 proposes to add something similar to ``@signature_dispatch`` to the 
python standard library, but appears to have been stalled for over a decade.
