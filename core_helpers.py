# core_helpers.py

def seconds_to_frames(seconds: float, fps: int) -> int:
    """Convert seconds to frame number using the given FPS."""
    return int(seconds * fps)
