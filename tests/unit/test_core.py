import os
import bpy
import pytest
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
import blender_core


def test_sec2frame():
    assert blender_core.sec2frame(1.5, 30) == 45


def test_finalize_frame_end(monkeypatch, strip_factory):
    blender_core.init_sequence(24)
    s1 = strip_factory(frame_start=1, length=5)
    s2 = strip_factory(frame_start=6, length=10)
    bpy.context.scene.sequence_editor.sequences_all.clear()
    bpy.context.scene.sequence_editor.sequences_all.extend([s1, s2])
    bpy.context.scene.render.image_settings = type("IS", (), {})()
    bpy.context.scene.render.ffmpeg = type("FF", (), {})()
    monkeypatch.setattr(os.path, "exists", lambda p: True)
    blender_core.finalize_render("out.mp4", 1920, 1080, 24)
    assert bpy.context.scene.frame_end == s2.frame_final_end
