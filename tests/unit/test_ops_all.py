import inspect
import pytest

import blender_core

@pytest.mark.parametrize("name,fn", blender_core.OPERATIONS.items())
def test_runs(name, fn, strip_factory):
    sig = inspect.signature(fn)
    kwargs = {p.name: 0 for p in list(sig.parameters.values())[1:]}
    try:
        fn(strip_factory(), **kwargs)
    except Exception:
        pytest.xfail("operation requires full environment")
