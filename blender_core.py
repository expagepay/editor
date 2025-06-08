import logging

from utils import audio, clips, transform

log = logging.getLogger(__name__)

OPERATIONS: dict[str, callable] = {}


def register(name: str):
    def _decorator(fn):
        OPERATIONS[name] = fn
        return fn
    return _decorator


@register("init_sequence")
def init_sequence(fps):
    return clips.init_sequence(fps)


@register("add_video_strip")
def add_video_strip(*args, **kwargs):
    return clips.add_video_strip(*args, **kwargs)


@register("add_audio_strip")
def add_audio_strip(*args, **kwargs):
    return audio.add_audio_strip(*args, **kwargs)


@register("add_image_strip")
def add_image_strip(*args, **kwargs):
    return clips.add_image_strip(*args, **kwargs)


@register("split_strip")
def split_strip(*args, **kwargs):
    return clips.split_strip(*args, **kwargs)


@register("delete_strip")
def delete_strip(*args, **kwargs):
    return clips.delete_strip(*args, **kwargs)


@register("merge_strips")
def merge_strips(*args, **kwargs):
    return clips.merge_strips(*args, **kwargs)


@register("transform_strip")
def transform_strip(*args, **kwargs):
    return transform.transform_strip(*args, **kwargs)


@register("finalize_render")
def finalize_render(*args, **kwargs):
    return clips.finalize_render(*args, **kwargs)


@register("split_video_strip")
def split_video_strip(*args, **kwargs):
    return clips.split_video_strip(*args, **kwargs)


@register("cut_video_strip")
def cut_video_strip(*args, **kwargs):
    return clips.cut_video_strip(*args, **kwargs)


@register("cut_video")
def cut_video(*args, **kwargs):
    return clips.cut_video(*args, **kwargs)


@register("split_audio_strip")
def split_audio_strip(*args, **kwargs):
    return audio.split_audio_strip(*args, **kwargs)


@register("cut_audio_strip")
def cut_audio_strip(*args, **kwargs):
    return audio.cut_audio_strip(*args, **kwargs)


@register("set_audio_volume")
def set_audio_volume(*args, **kwargs):
    return audio.set_audio_volume(*args, **kwargs)


@register("extract_audio_from_video")
def extract_audio_from_video(*args, **kwargs):
    return audio.extract_audio_from_video(*args, **kwargs)


@register("rotate_strip")
def rotate_strip(*args, **kwargs):
    return transform.rotate_strip(*args, **kwargs)


@register("translate_strip")
def translate_strip(*args, **kwargs):
    return transform.translate_strip(*args, **kwargs)


__all__ = list(OPERATIONS.keys())
