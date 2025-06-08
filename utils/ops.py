from . import audio, clips
from .common import ensure_editor, sec2frame, log


def add_media(path: str, *, channel: int = 1, start_sec: float = 0.0,
              end_sec: float | None = None, fps: int = 24):
    """Add a video, image or audio strip using seconds for positioning."""
    frame_start = sec2frame(start_sec, fps)
    lower = path.lower()

    if lower.endswith((".mp3", ".wav", ".aac", ".flac", ".ogg")):
        strip = audio.add_audio_strip(path, channel=channel, frame_start=frame_start)
    elif lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tga", ".gif")):
        frame_end = sec2frame(end_sec, fps) if end_sec is not None else None
        strip = clips.add_image_strip(path, channel=channel,
                                      frame_start=frame_start,
                                      frame_end=frame_end)
    else:
        strip = clips.add_video_strip(path, channel=channel, frame_start=frame_start)
        if end_sec is not None:
            strip.frame_final_end = frame_start + sec2frame(end_sec - start_sec, fps)
    return strip


def cut_between(strip_name: str, start_sec: float, end_sec: float, fps: int):
    """Cut and remove the region between ``start_sec`` and ``end_sec``."""
    scene = ensure_editor()
    strip = scene.sequence_editor.sequences_all.get(strip_name)
    if not strip:
        raise ValueError(f"Strip '{strip_name}' não encontrado para cut.")

    if getattr(strip, "type", "").upper() == "SOUND":
        return audio.cut_audio_strip(strip_name, start_sec, end_sec, fps)
    return clips.cut_video_strip(strip_name, start_sec, end_sec, fps)


def split_at(strip_name: str, times: list[float], fps: int):
    """Split a strip at the given times without removing any parts."""
    scene = ensure_editor()
    strip = scene.sequence_editor.sequences_all.get(strip_name)
    if not strip:
        raise ValueError(f"Strip '{strip_name}' não encontrado para split.")

    if getattr(strip, "type", "").upper() == "SOUND":
        return audio.split_audio_strip(strip_name, times, fps)
    return clips.split_video_strip(strip_name, times, fps)


__all__ = [
    "add_media",
    "cut_between",
    "split_at",
]
