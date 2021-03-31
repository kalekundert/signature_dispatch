******************
Signature Dispatch
******************

``signature_dispatch`` is a simple python utility for executing the first of 
many functions whose signature matches the set of given arguments.

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
  >>> 
  >>> @dispatch
  ... def f(x, y):
  ...    return x, y
  ...

When called, all of the decorated functions will be tested in order to see if 
they accept the given arguments.  The first one that does will be invoked.  A 
TypeError will be raised if none of the functions can accept the arguments::

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

Each decorated function will be replaced by the same callable.  To avoid 
confusion, then, it's best to use the same name for each function.  The 
docstring of the ultimate callable will be taken from the final decorated 
function.

