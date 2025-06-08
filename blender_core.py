import logging

from utils import audio, clips, transform
from utils.common import sec2frame
from utils.ops import add_media, cut_between, split_at

log = logging.getLogger(__name__)


def init_sequence(fps: int):
    """Initialize the VSE with the given FPS."""
    return clips.init_sequence(fps)


# re-export helpers directly for external use
add_video_strip = clips.add_video_strip
add_audio_strip = audio.add_audio_strip
add_image_strip = clips.add_image_strip
delete_strip = clips.delete_strip
merge_strips = clips.merge_strips
transform_strip = transform.transform_strip
rotate_strip = transform.rotate_strip
translate_strip = transform.translate_strip
set_audio_volume = audio.set_audio_volume
extract_audio_from_video = audio.extract_audio_from_video
finalize_render = clips.finalize_render

__all__ = [
    "sec2frame",
    "init_sequence",
    "add_media",
    "add_video_strip",
    "add_audio_strip",
    "add_image_strip",
    "delete_strip",
    "merge_strips",
    "transform_strip",
    "rotate_strip",
    "translate_strip",
    "set_audio_volume",
    "extract_audio_from_video",
    "cut_between",
    "split_at",
    "finalize_render",
]
