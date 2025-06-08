import bpy
import logging

log = logging.getLogger(__name__)


def ensure_editor():
    scene = bpy.context.scene
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    return scene


def sec2frame(seconds: float, fps: int) -> int:
    """Convert seconds to an integer frame number."""
    return int(seconds * fps)
