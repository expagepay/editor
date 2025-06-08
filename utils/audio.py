import os
import bpy

from .common import ensure_editor, log


def add_audio_strip(audio_path, channel=2, frame_start=1):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Áudio não encontrado: {audio_path}")
    scene = ensure_editor()
    strip = scene.sequence_editor.sequences.new_sound(
        name=os.path.splitext(os.path.basename(audio_path))[0],
        filepath=audio_path,
        channel=int(channel),
        frame_start=int(frame_start)
    )
    if strip.frame_final_end - strip.frame_start <= 2:
        log.warning("Atenção: áudio '%s' tem duração parecendo curta: end=%s", strip.name, strip.frame_final_end)
    log.debug("Adicionado áudio '%s' start=%s end=%s", strip.name, strip.frame_final_start, strip.frame_final_end)
    return strip


def split_audio_strip(strip_name: str, split_times: list, fps: int) -> list:
    scene = ensure_editor()
    seqs = scene.sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if strip is None:
        raise ValueError(f"Strip de áudio '{strip_name}' não encontrado para split.")

    frames = sorted(int(t * fps) for t in split_times)
    for f in reversed(frames):
        scene.frame_current = f
        bpy.ops.sequencer.select_all(action='DESELECT')
        strip.select = True
        bpy.ops.sequencer.split(frame=f, type='SOFT', side='LEFT')

    new_strips = [s.name for s in seqs if s.name.startswith(strip_name)]
    log.debug("Split em áudio '%s' nos frames %s, gerou: %s", strip_name, frames, new_strips)
    return new_strips


def cut_audio_strip(strip_name: str, start_time: float, end_time: float, fps: int) -> str:
    scene = ensure_editor()
    seqs = scene.sequence_editor.sequences_all
    orig = seqs.get(strip_name)
    if orig is None:
        raise ValueError(f"Strip de áudio '{strip_name}' não encontrado para cut.")

    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)

    scene.frame_current = end_frame
    bpy.ops.sequencer.select_all(action='DESELECT')
    orig.select = True
    bpy.ops.sequencer.split(frame=end_frame, type='SOFT', side='LEFT')
    seqs = scene.sequence_editor.sequences_all
    before_end = seqs.get(strip_name)
    after_end = next((s for s in seqs if s.name.startswith(strip_name + ".00") and s.frame_final_start > end_frame), None)

    scene.frame_current = start_frame
    bpy.ops.sequencer.select_all(action='DESELECT')
    before_end.select = True
    bpy.ops.sequencer.split(frame=start_frame, type='SOFT', side='LEFT')
    seqs = scene.sequence_editor.sequences_all
    before_start = seqs.get(strip_name)
    middle = next((s for s in seqs if s.name.startswith(strip_name + ".00") and s.frame_final_end <= end_frame), None)
    after_middle = next((s for s in seqs if s.name.startswith(strip_name + ".00") and s.frame_final_start >= end_frame), None)

    to_delete = []
    if before_start:
        to_delete.append(before_start.name)
    if after_end:
        to_delete.append(after_end.name)
    if after_middle and after_middle.name not in to_delete:
        to_delete.append(after_middle.name)

    for name in to_delete:
        s = seqs.get(name)
        if s:
            bpy.ops.sequencer.select_all(action='DESELECT')
            s.select = True
            bpy.ops.sequencer.delete()
            log.debug("cut_audio_strip: Removido '%s'", name)

    if middle:
        new_name = f"{strip_name}_cut"
        middle.name = new_name
        log.debug("cut_audio_strip: Strip resultante '%s' (start=%s, end=%s)", new_name, start_time, end_time)
        return new_name
    raise RuntimeError(f"cut_audio_strip: Não foi possível encontrar trecho intermediário para '{strip_name}'.")


def set_audio_volume(strip_name: str, volume_percent: float):
    seqs = ensure_editor().sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if strip is None:
        raise ValueError(f"Strip de áudio '{strip_name}' não encontrado para ajuste de volume.")

    vol = max(0.0, min(volume_percent / 100.0, 2.0))
    strip.volume = vol
    log.debug("set_audio_volume: Strip '%s' volume ajustado para %s%%", strip_name, volume_percent)


def extract_audio_from_video(video_strip_name: str, channel: int = 1, frame_start: int = 1) -> str:
    seqs = ensure_editor().sequence_editor.sequences_all
    vstrip = seqs.get(video_strip_name)
    if vstrip is None:
        raise ValueError(f"Strip de vídeo '{video_strip_name}' não encontrado para extrair áudio.")

    video_path = vstrip.filepath
    scene = bpy.context.scene
    scene.frame_current = vstrip.frame_start
    bpy.ops.sequencer.sound_strip_add(
        filepath=video_path,
        channel=int(channel),
        frame_start=int(vstrip.frame_start),
    )
    new_audio = scene.sequence_editor.sequences_all[-1]
    new_name = f"{video_strip_name}_audio"
    new_audio.name = new_name
    log.debug("extract_audio_from_video: '%s' criado a partir de '%s'", new_name, video_strip_name)
    return new_name


