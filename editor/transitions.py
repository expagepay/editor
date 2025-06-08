from moviepy.editor import concatenate_videoclips
from .models import Clip
from typing import Any

def crossfade(clips: list, duration: float) -> Any:
    """Crossfade transition between a list of VideoFileClip."""
    return concatenate_videoclips(clips, method='compose', padding=-duration)
