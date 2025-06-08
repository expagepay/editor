import shutil
import os
import runpy
import sys
import types

from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2]))
from generate_project import generate_project_file
import blender_core


def test_json_flow(tmp_path, project_root, prepare_assets, monkeypatch):
    # copy required scripts into temp dir
    shutil_src = project_root / "blender_script_template.py"
    core_src = project_root / "blender_core.py"
    shutil.copy(shutil_src, tmp_path / "blender_script_template.py")
    shutil.copy(core_src, tmp_path / "blender_core.py")

    video = prepare_assets / "video.mp4"
    audio = prepare_assets / "audio.wav"

    config = {
        "videos": [{"path": str(video), "channel": 1, "start_frame": 1, "name": "vid"}],
        "audios": [{"path": str(audio), "channel": 2, "start_frame": 1, "name": "aud"}],
        "images": [],
        "output_path": "output/final.mp4",
        "resolution_x": 64,
        "resolution_y": 64,
        "fps": 24,
        "operations": []
    }

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        generate_project_file(config)

        # Prepare fake bpy for this integration test
        seq_data = []
        fake_bpy = types.SimpleNamespace(
            context=types.SimpleNamespace(scene=types.SimpleNamespace(
                sequence_editor=types.SimpleNamespace(sequences_all=seq_data),
                sequence_editor_create=lambda: None,
                render=types.SimpleNamespace()
            )),
            data=types.SimpleNamespace(movieclips=types.SimpleNamespace(
                load=lambda p: types.SimpleNamespace(frame_duration=24),
                remove=lambda x: None
            )),
            ops=types.SimpleNamespace(
                render=types.SimpleNamespace(render=lambda animation=True: None),
                sequencer=types.SimpleNamespace(select_all=lambda action=None: None,
                                                delete=lambda: None,
                                                split=lambda frame=None, type=None, side=None: None,
                                                meta_make=lambda: None)
            )
        )
        monkeypatch.setitem(sys.modules, "bpy", fake_bpy)
        import importlib
        importlib.reload(blender_core)

        # stub all blender_core functions to just append calls

        def fake_init_sequence(fps):
            fake_bpy.context.scene.sequence_editor.sequences_all = []
            return fake_bpy.context.scene.sequence_editor.sequences_all

        def fake_add_video_strip(path, channel=1, frame_start=1):
            seq = types.SimpleNamespace(name=os.path.basename(path))
            fake_bpy.context.scene.sequence_editor.sequences_all.append(seq)
            return seq

        def fake_add_audio_strip(path, channel=2, frame_start=1):
            seq = types.SimpleNamespace(name=os.path.basename(path))
            fake_bpy.context.scene.sequence_editor.sequences_all.append(seq)
            return seq

        def fake_add_image_strip(path, channel=3, frame_start=1, frame_end=None):
            seq = types.SimpleNamespace(name=os.path.basename(path))
            fake_bpy.context.scene.sequence_editor.sequences_all.append(seq)
            return seq

        monkeypatch.setattr(blender_core, "init_sequence", fake_init_sequence)
        blender_core.OPERATIONS["init_sequence"] = fake_init_sequence
        monkeypatch.setattr(blender_core, "add_video_strip", fake_add_video_strip)
        blender_core.OPERATIONS["add_video_strip"] = fake_add_video_strip
        monkeypatch.setattr(blender_core, "add_audio_strip", fake_add_audio_strip)
        blender_core.OPERATIONS["add_audio_strip"] = fake_add_audio_strip
        monkeypatch.setattr(blender_core, "add_image_strip", fake_add_image_strip)
        blender_core.OPERATIONS["add_image_strip"] = fake_add_image_strip
        monkeypatch.setattr(blender_core, "split_strip", lambda *a, **k: None)
        blender_core.OPERATIONS["split_strip"] = lambda *a, **k: None
        monkeypatch.setattr(blender_core, "delete_strip", lambda *a, **k: None)
        blender_core.OPERATIONS["delete_strip"] = lambda *a, **k: None
        monkeypatch.setattr(blender_core, "merge_strips", lambda *a, **k: None)
        blender_core.OPERATIONS["merge_strips"] = lambda *a, **k: None
        monkeypatch.setattr(blender_core, "transform_strip", lambda *a, **k: None)
        blender_core.OPERATIONS["transform_strip"] = lambda *a, **k: None
        fake_finalize = lambda *a, **k: None
        monkeypatch.setattr(blender_core, "finalize_render", fake_finalize)
        blender_core.OPERATIONS["finalize_render"] = fake_finalize


        runpy.run_path(str(tmp_path / "blender_script.py"), run_name="__main__")
        assert len(fake_bpy.context.scene.sequence_editor.sequences_all) >= 2
    finally:
        os.chdir(cwd)
