import bpy
from utils.time_utils import sec2frame
from typing import Literal, Optional

MediaType = Literal["video", "image", "audio"]


def add_media(path: str,
              media_type: MediaType,
              start_sec: float,
              end_sec: Optional[float] = None,
              channel: int = 1) -> bpy.types.Sequence:
    scene = bpy.context.scene
    fps = scene.render.fps
    start = sec2frame(start_sec, fps)
    end = sec2frame(end_sec, fps) if end_sec else None

    op = {
        "video": bpy.ops.sequencer.movie_strip_add,
        "image": bpy.ops.sequencer.image_strip_add,
        "audio": bpy.ops.sequencer.sound_strip_add,
    }[media_type]

    op(filepath=path, frame_start=start, channel=channel, overlap=False)
    strip = bpy.context.selected_sequences[-1]
    if end:
        strip.frame_final_end = end
    return strip


def split_at(strip: bpy.types.Sequence, *times: float) -> None:
    fps = bpy.context.scene.render.fps
    for t in times:
        frame = sec2frame(t, fps)
        bpy.context.scene.frame_current = frame
        strip.select = True
        bpy.ops.sequencer.split(frame=frame, side='NO_CHANGE', use_cursor_position=False)


def cut_between(strip: bpy.types.Sequence, t0: float, t1: float) -> None:
    split_at(strip, t0, t1)
    # após dois splits, o trecho intermediário vira strip ativo → deletar
    mid = bpy.context.selected_sequences[-1]
    bpy.ops.sequencer.delete()


def transform_strip(strip: bpy.types.Sequence,
                    translate: tuple[float, float] = (0, 0),
                    rotation: float = 0.0,
                    scale: float = 1.0) -> bpy.types.Sequence:
    scene = bpy.context.scene
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    trans = scene.sequence_editor.sequences.new_effect(
        name=f"Transform_{strip.name}",
        type='TRANSFORM',
        channel=strip.channel + 1,
        frame_start=int(strip.frame_start),
        frame_end=int(strip.frame_final_end),
        seq1=strip,
    )
    dx, dy = translate
    trans.translate_start_x = int(dx)
    trans.translate_start_y = int(dy)
    trans.rotation_start = float(rotation)
    trans.scale_start_x = trans.scale_start_y = float(scale)
    return trans


__all__ = [
    "sec2frame",
    "add_media",
    "split_at",
    "cut_between",
    "transform_strip",
]
