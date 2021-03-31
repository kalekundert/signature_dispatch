#!/usr/bin/env python3

import signature_dispatch
import pytest

def test_positional_or_keyword():
    d = signature_dispatch()

    @d
    def f(a):
        return a
    @d
    def f(a, b):
        return a, b

    assert f(1) == 1
    assert f(a=1) == 1

    assert f(1, 2) == (1, 2)
    assert f(1, b=2) == (1, 2)
    assert f(a=1, b=2) == (1, 2)

    with pytest.raises(TypeError):
        f()
    with pytest.raises(TypeError):
        f(1, 2, 3)

def test_var_positional():
    d = signature_dispatch()

    @d
    def f(*a):
        return a
    @d
    def f(*a, b):
        return a, b

    assert f() == ()
    assert f(1) == (1,)
    assert f(1, 2) == (1, 2)

    assert f(b=1) == ((), 1)
    assert f(1, b=2) == ((1,), 2)
    assert f(1, 2, b=3) == ((1, 2), 3)

    with pytest.raises(TypeError):
        f(c=1)

def test_keyword_only():
    d = signature_dispatch()

    @d
    def f(*, a):
        return a
    @d
    def f(*, a, b):
        return a, b

    assert f(a=1) == 1
    assert f(a=1, b=2) == (1, 2)

    with pytest.raises(TypeError):
        f()
    with pytest.raises(TypeError):
        f(1)
    with pytest.raises(TypeError):
        f(b=1)

def test_var_keyword():
    d = signature_dispatch()

    @d
    def f(**kwargs):
        return kwargs
    @d
    def f(a, **kwargs):
        return a, kwargs

    assert f() == {}
    assert f(a=1) == {'a': 1}
    assert f(b=1) == {'b': 1}
    assert f(a=1, b=2) == {'a': 1, 'b': 2}

    assert f(1) == (1, {})
    assert f(1, b=2) == (1, {'b': 2})
    assert f(1, c=2) == (1, {'c': 2})
    assert f(1, b=2, c=3) == (1, {'b': 2, 'c': 3})

    with pytest.raises(TypeError):
        f(1, 2)
    with pytest.raises(TypeError):
        f(1, a=2)  # `a` specified twice

def test_docstring():
    d = signature_dispatch()

    @d
    def f(a):
        "a"
        return a
    @d
    def f(a, b):
        "a, b"
        return a, b

    assert f.__doc__ == "a, b"

def test_error_message():
    d = signature_dispatch()

    @d
    def f(a):
        return a
    @d
    def f(a, b):
        return a, b

    with pytest.raises(TypeError) as err:
        f()

    assert err.match(r"(?m)can't dispatch the given arguments to any of the candidate functions:")
    assert err.match(r"(?m)arguments: $")
    assert err.match(r"(?m)candidates:$")
    assert err.match(r"(?m)\(a\): missing a required argument: 'a'$")
    assert err.match(r"(?m)\(a, b\): missing a required argument: 'a'$")

    with pytest.raises(TypeError) as err:
        f(1, 2, 3)

    assert err.match(r"(?m)can't dispatch the given arguments to any of the candidate functions:")
    assert err.match(r"(?m)arguments: 1, 2, 3$")
    assert err.match(r"(?m)candidates:$")
    assert err.match(r"(?m)\(a\): too many positional arguments$")
    assert err.match(r"(?m)\(a, b\): too many positional arguments$")

def test_function_raises_type_error():
    d = signature_dispatch()

    @d
    def f(a):
        raise TypeError("my error")
    @d
    def f(a):
        return a

    with pytest.raises(TypeError, match="my error"):
        f(1)
