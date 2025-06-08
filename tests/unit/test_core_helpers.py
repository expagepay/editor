import pytest, sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from core_helpers import seconds_to_frames
from blender_core import add_video_strip


def test_seconds_to_frames():
    assert seconds_to_frames(2.5, 24) == 60


def test_add_video_strip_missing(tmp_path):
    missing = tmp_path / "no_video.mp4"
    with pytest.raises(FileNotFoundError):
        add_video_strip(str(missing))
