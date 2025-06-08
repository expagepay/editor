from .timeline import Timeline
from .renderer import Renderer
from .models import Clip
from .effects import apply_fade
from .transitions import crossfade
from typing import List, Dict, Any

class Editor:
    """Main entry point to build or modify a project."""
    def __init__(self):
        self.timeline = Timeline()
        self.renderer = Renderer(self.timeline)

    def add_clip(self, media_type: str, file_path: str, layer: int, start: float, end: float = None, duration: float = None) -> Dict:
        """Add video, audio, or image to timeline."""
        if media_type == 'video':
            clip = Clip.from_video(file_path, start=start, end=end)
        elif media_type == 'audio':
            clip = Clip.from_audio(file_path, start=start, end=end)
        elif media_type == 'image':
            assert duration is not None, "Duration required for images"
            clip = Clip.from_image(file_path, duration=duration, start=start)
        else:
            raise ValueError(f"Unknown media type: {media_type}")

        self.timeline.add_clip(clip, layer)
        return self.get_state()

    def apply_operation(self, op: Dict[str, Any]) -> Dict:
        """Execute a single operation: cut, fade, transition, etc."""
        action = op.get('action')
        params = op.get('params', {})
        if action == 'fade':
            layer, index, fade_type, duration = params.values()
            clips = self.timeline.clips[layer]
            target = clips[index]
            target.clip = apply_fade(target.clip, start=target.start, duration=duration, fade_type=fade_type)
        elif action == 'crossfade':
            clips = [c.clip for c in self.timeline.clips[params['layer']]]
            new = crossfade(clips, params['duration'])
            self.timeline.clips[params['layer']] = [Clip(type='video', clip=new, layer=params['layer'], start=0, end=None)]
        else:
            raise ValueError(f"Unknown operation: {action}")

        return self.get_state()

    def execute_operations(self, ops: List[Dict[str, Any]]) -> Dict:
        state = {}
        for op in ops:
            state = self.apply_operation(op)
        return state

    def load_timeline_from_json(self, json_path: str) -> Dict:
        import json
        with open(json_path, 'r') as f:
            data = json.load(f)
        for op in data.get('operations', []):
            self.apply_operation(op)
        return self.get_state()

    def get_state(self) -> Dict:
        """Returns current state summary after each step."""
        return self.timeline.export_state()

    def render(self, output_path: str, fps: int = 24) -> None:
        self.renderer.render(output_path, fps)
