from moviepy.editor import VideoClip
from moviepy.video.fx.all import fadein, fadeout, resize
from .models import Clip
from typing import Any, Dict

def apply_fade(clip: Any, start: float, duration: float, fade_type: str = 'in') -> Any:
    """Apply fade-in or fade-out on a clip."""
    if fade_type == 'in':
        return fadein(clip, duration)
    else:
        return fadeout(clip, duration)
