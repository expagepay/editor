import importlib
import blender_core
from unittest import mock


def test_ensure_called(strip_factory):
    importlib.reload(blender_core)
    with mock.patch.object(blender_core, "_ensure_editor", wraps=blender_core._ensure_editor) as spy:
        blender_core.transform_strip(strip_factory())
        assert spy.call_count == 1
