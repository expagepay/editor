from moviepy.editor import CompositeVideoClip, CompositeAudioClip
from .timeline import Timeline
import logging

logger = logging.getLogger(__name__)

class Renderer:
    """Composes all layers and renders the final video."""
    def __init__(self, timeline: Timeline):
        self.timeline = timeline

    def render(self, output_path: str, fps: int = 24) -> None:
        """Renders timeline to a single output file."""
        video_clips = []
        audio_clips = []

        for layer, clips in sorted(self.timeline.clips.items()):
            for c in clips:
                mc = c.clip.set_start(c.start)
                if c.type in ('video', 'image'):
                    video_clips.append(mc)
                else:
                    audio_clips.append(mc)

        if not video_clips:
            logger.error("No video or image clips to render.")
            return

        composite = CompositeVideoClip(video_clips)
        if audio_clips:
            composite = composite.set_audio(CompositeAudioClip(audio_clips))

        composite.write_videofile(output_path, fps=fps)
