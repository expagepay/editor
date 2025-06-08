import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from generate_project import generate_project_file


def test_generate_project_file(tmp_path):
    config = {
        "videos": [],
        "audios": [],
        "images": [],
        "operations": []
    }

    template_src = os.path.join(os.path.dirname(__file__), os.pardir, "blender_script_template.py")
    template_dst = tmp_path / "blender_script_template.py"
    shutil.copy(template_src, template_dst)

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        generate_project_file(config)
        assert (tmp_path / "config" / "project_config.json").exists()
        assert (tmp_path / "blender_script.py").exists()
        with open(tmp_path / "config" / "project_config.json") as f:
            data = json.load(f)
        assert data == config
    finally:
        os.chdir(cwd)

