import blender_core


def test_ensure_called(mocker, strip_factory):
    spy = mocker.spy(blender_core, "_ensure_editor")
    blender_core.transform_strip(strip_factory())
    assert spy.call_count == 1
