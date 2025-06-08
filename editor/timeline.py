from typing import Dict, List
from .models import Clip

class Timeline:
    """Manages clips organized by layers."""
    def __init__(self):
        self.clips: Dict[int, List[Clip]] = {}

    def add_clip(self, clip: Clip, layer: int) -> None:
        """Adds a clip to a given layer."""
        clip.layer = layer
        self.clips.setdefault(layer, []).append(clip)

    def export_state(self) -> Dict:
        """Returns a summary of current timeline state."""
        state = []
        for layer, clips in self.clips.items():
            for c in clips:
                state.append({
                    'type': c.type,
                    'layer': layer,
                    'start': c.start,
                    'end': c.end if c.end is not None else c.clip.duration,
                    'duration': c.clip.duration,
                })
        return {'clips': state}

    def load_from_json(self, json_data: dict) -> None:
        """Imports a timeline defined in JSON format."""
        for op in json_data.get('operations', []):
            pass  # will be handled in core
