import os
import shutil
import runpy
import sys
from pathlib import Path

import blender_core
from generate_project import generate_project_file
from tests import conftest


def test_ops_json(tmp_path, project_root, prepare_assets):
    shutil.copy(project_root / "blender_script_template.py", tmp_path / "blender_script_template.py")
    shutil.copy(project_root / "blender_core.py", tmp_path / "blender_core.py")

    ops = []
    for name in blender_core.OPERATIONS:
        if name in {"init_sequence", "add_video_strip", "add_audio_strip", "add_image_strip", "finalize_render"}:
            continue
        if name in {"split_video_strip", "cut_video_strip", "rotate_strip", "translate_strip", "transform_strip"}:
            target = "vid"
        else:
            target = "aud"
        entry = {"type": name, "target": target}
        ops.append(entry)

    config = {
        "videos": [{"path": str(prepare_assets / "video.mp4"), "channel": 1, "start_frame": 1, "name": "vid"}],
        "audios": [{"path": str(prepare_assets / "audio.wav"), "channel": 2, "start_frame": 1, "name": "aud"}],
        "images": [],
        "output_path": "output/final.mp4",
        "resolution_x": 64,
        "resolution_y": 64,
        "fps": 24,
        "operations": ops,
    }

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        generate_project_file(config)
        conftest._mock_bpy()
        import importlib
        importlib.reload(blender_core)
        fake_finalize = lambda *a, **k: None
        blender_core.finalize_render = fake_finalize
        blender_core.OPERATIONS["finalize_render"] = fake_finalize
        runpy.run_path(str(tmp_path / "blender_script.py"), run_name="__main__")
    finally:
        os.chdir(cwd)
