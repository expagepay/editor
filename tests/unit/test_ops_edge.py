import pytest
import blender_core

@pytest.mark.parametrize("frame", [-1, 100000])
@pytest.mark.xfail(reason="edge cases not handled")
def test_split_strip_out_of_range(strip_factory, frame):
    blender_core.split_strip(strip_factory(), frame)
