#!/usr/bin/env python3

import signature_dispatch
import pytest

def test_positional_only():
    d = signature_dispatch()

    @d
    def f(a, /):
        return a
    @d
    def f(a, b, /):
        return a, b

    assert f(1) == 1
    assert f(1, 2) == (1, 2)

    with pytest.raises(TypeError):
        f()
    with pytest.raises(TypeError):
        f(1, 2, 3)
    with pytest.raises(TypeError):
        f(a=1)
    with pytest.raises(TypeError):
        f(1, b=2)
    with pytest.raises(TypeError):
        f(a=1, b=2)


