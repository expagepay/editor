import bpy
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))

from blender_core import sec2frame, add_media


def test_sec2frame():
    assert sec2frame(1.0, 30) == 30


def test_add_media_sets_frames(tmp_path):
    dummy = tmp_path / "dummy.png"
    dummy.write_text("x")
    bpy.context.scene.render.fps = 30
    bpy.context.scene.sequence_editor_create()
    strip = add_media(str(dummy), "image", 2.5, 4.0, 5)
    assert strip.frame_start == 75 and strip.frame_final_end == 120
