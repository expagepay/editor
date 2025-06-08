from typing import Dict

def seconds_to_frames(seconds: float, fps: int = 24) -> int:
    return int(seconds * fps)


def frames_to_seconds(frames: int, fps: int = 24) -> float:
    return frames / fps
