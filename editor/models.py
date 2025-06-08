from dataclasses import dataclass
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip
from typing import Optional, Any

@dataclass
class Clip:
    """Represents a media clip on the timeline."""
    type: str
    clip: Any
    layer: int
    start: float
    end: Optional[float]

    @classmethod
    def from_video(cls, file_path: str, start: float = 0.0, end: Optional[float] = None) -> "Clip":
        video = VideoFileClip(file_path)
        sub = video.subclip(start, end) if end is not None else video.subclip(start)
        return cls(type='video', clip=sub, layer=0, start=start, end=end)

    @classmethod
    def from_audio(cls, file_path: str, start: float = 0.0, end: Optional[float] = None) -> "Clip":
        audio = AudioFileClip(file_path)
        sub = audio.subclip(start, end) if end is not None else audio.subclip(start)
        return cls(type='audio', clip=sub, layer=0, start=start, end=end)

    @classmethod
    def from_image(cls, file_path: str, duration: float, start: float = 0.0) -> "Clip":
        img = ImageClip(file_path).set_duration(duration)
        return cls(type='image', clip=img, layer=0, start=start, end=start + duration)
