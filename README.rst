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
Create a dispatcher and use it to decorate multiple functions.  Note that the 
module itself is directly invoked to create a dispatcher::

  >>> import signature_dispatch
  >>> dispatch = signature_dispatch()
  >>> @dispatch
  ... def f(x):
  ...    return x
  ...
  >>> @dispatch
  ... def f(x, y):
  ...    return x, y
  ...

When called, all of the decorated functions will be tested in order to see if 
they match the given arguments.  The first one that does will be invoked.  A 
``TypeError`` will be raised if no matches are found::

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

Type annotations are taken into account when choosing which function to 
invoke::

  >>> from typing import List
  >>> dispatch = signature_dispatch()
  >>> @dispatch
  ... def g(x: int):
  ...    return 'int', x
  ...
  >>> @dispatch
  ... def f(x: List[int]):
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

Each decorated function will be replaced by the same callable.  To avoid 
confusion, then, it's best to use the same name for each function.  The 
docstring of the ultimate callable will be taken from the final decorated 
function.

Applications
============
Writing decorators that can *optionally* be given arguments is tricky to get 
right, but ``signature_dispatch`` makes it easy.  For example, here is a 
decorator that prints a message to the terminal every time a function is called 
and optionally accepts an extra message to print::

  >>> def log(*args, **kwargs):
  ...     import signature_dispatch
  ...     from functools import wraps, partial
  ...
  ...     dispatch = signature_dispatch()
  ...
  ...     @dispatch
  ...     def decorator(*, msg):
  ...         return partial(wrap, msg=msg)
  ...
  ...     @dispatch
  ...     def decorator(f):
  ...         return wrap(f)
  ...
  ...     def wrap(f, msg=None):
  ...
  ...         @wraps(f)
  ...         def wrapper(*args, **kwargs):
  ...             print(f.__name__)
  ...             if msg: print(msg)
  ...             return f()
  ...
  ...         return wrapper
  ...
  ...     return decorator(*args, **kwargs)

Using ``@log`` without an argument::

  >>> @log
  ... def foo():
  ...     pass
  >>> foo()
  foo

Using ``@log`` with an argument::

  >>> @log(msg="Hello world!")
  ... def bar():
  ...     pass
  >>> bar()
  bar
  Hello world!

Alternatives
============
The dispatching_ library does almost the same thing as this one, with a few 
small differences:

- The API is slightly more verbose.
- Subscripted generic types (e.g. ``List[int]``) are not supported.
- Annotations can be arbitrary functions.

.. _dispatching: https://github.com/Lucretiel/Dispatch
