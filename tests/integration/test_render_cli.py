import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2]))
from generate_project import generate_project_file

blender = shutil.which("blender")
if not blender:
    pytest.skip("Blender CLI not installed", allow_module_level=True)


def test_render_cli(tmp_path, project_root, prepare_assets):
    shutil.copy(project_root / "blender_script_template.py", tmp_path / "blender_script_template.py")
    shutil.copy(project_root / "blender_core.py", tmp_path / "blender_core.py")

    config = {
        "videos": [{"path": str(prepare_assets / "video.mp4"), "channel": 1, "start_frame": 1, "name": "vid"}],
        "audios": [{"path": str(prepare_assets / "audio.wav"), "channel": 2, "start_frame": 1, "name": "aud"}],
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
        cmd = [
            blender,
            "-b",
            "-P",
            "blender_script_template.py",
            "--",
            "config/project_config.json",
        ]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=180,
        )
        assert result.returncode == 0
        out = result.stdout.decode("utf-8", errors="ignore")
        assert "Finished Rendering" in out
        out = tmp_path / "output" / "final.mp4"
        assert out.exists()
        assert out.stat().st_size > 0
    finally:
        os.chdir(cwd)
