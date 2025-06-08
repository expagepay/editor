import os
import bpy

from .common import ensure_editor, log


def init_sequence(fps):
    scene = bpy.context.scene
    scene.render.fps = fps
    if scene.sequence_editor:
        bpy.ops.sequencer.select_all(action='SELECT')
        bpy.ops.sequencer.delete()
    scene.sequence_editor_create()
    return scene.sequence_editor.sequences_all


def add_video_strip(video_path, channel=1, frame_start=1):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")
    scene = ensure_editor()
    strip = scene.sequence_editor.sequences.new_movie(
        name=os.path.splitext(os.path.basename(video_path))[0],
        filepath=video_path,
        channel=int(channel),
        frame_start=int(frame_start)
    )
    try:
        mc = bpy.data.movieclips.load(video_path)
        duration_frames = int(mc.frame_duration)
        strip.frame_final_end = strip.frame_start + int(duration_frames)
        bpy.data.movieclips.remove(mc)
    except Exception as e:
        log.warning("Não foi possível ajustar duração do vídeo '%s': %s", video_path, e)
    log.debug("Adicionado vídeo '%s' start=%s end=%s", strip.name, strip.frame_final_start, strip.frame_final_end)
    return strip


def add_image_strip(image_path, channel=3, frame_start=1, frame_end=None):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")
    scene = ensure_editor()
    strip = scene.sequence_editor.sequences.new_image(
        name=os.path.splitext(os.path.basename(image_path))[0],
        filepath=image_path,
        channel=int(channel),
        frame_start=int(frame_start)
    )
    if frame_end is not None:
        strip.frame_final_end = int(frame_end)
    else:
        strip.frame_final_end = strip.frame_start + 100
    log.debug("Adicionado imagem '%s' start=%s end=%s", strip.name, strip.frame_start, strip.frame_final_end)
    return strip


def delete_strip(strip_name):
    seqs = ensure_editor().sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if strip:
        bpy.ops.sequencer.select_all(action='DESELECT')
        strip.select = True
        bpy.ops.sequencer.delete()
        log.debug("Strip '%s' deletado", strip_name)
    else:
        log.debug("Strip '%s' não encontrado para deletar", strip_name)


def merge_strips(strip_names, output_name="MergedMeta"):
    seqs = ensure_editor().sequence_editor.sequences_all
    bpy.ops.sequencer.select_all(action='DESELECT')
    for name in strip_names:
        s = seqs.get(name)
        if s:
            s.select = True
    bpy.ops.sequencer.meta_make()
    meta = [s for s in seqs if s.type == 'META' and s.name.startswith("Meta")][0]
    meta.name = output_name
    log.debug("Meta Strip '%s' criado com: %s", output_name, strip_names)
    return meta


def finalize_render(output_path, res_x, res_y, fps):
    scene = ensure_editor()
    scene.render.resolution_x = int(res_x)
    scene.render.resolution_y = int(res_y)
    scene.render.fps = int(fps)
    if not output_path.lower().endswith(".mp4"):
        output_path = os.path.join(output_path, "output.mp4")
    output_path = os.path.abspath(output_path)
    scene.render.filepath = output_path

    scene.render.use_sequencer = True
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.audio_codec = 'AAC'
    scene.render.ffmpeg.video_bitrate = 8000
    scene.render.ffmpeg.audio_bitrate = 192
    scene.render.ffmpeg.audio_channels = 'STEREO'

    seqs = scene.sequence_editor.sequences_all
    if seqs:
        scene.frame_start = 1
        scene.frame_end = max(int(s.frame_final_end) for s in seqs)
        log.debug("Range de frames: %s → %s", scene.frame_start, scene.frame_end)
    else:
        scene.frame_start = 1
        scene.frame_end = 100
        log.warning("Nenhum strip encontrado, usando 100 frames de fallback.")

    log.info("Renderizando para: %s", output_path)
    bpy.ops.render.render(animation=True)

    if os.path.exists(output_path):
        log.info("Render concluído: %s", output_path)
    else:
        log.error("Falha no render: arquivo não foi criado.")


def split_video_strip(strip_name: str, split_times: list, fps: int) -> list:
    scene = ensure_editor()
    seqs = scene.sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if strip is None:
        raise ValueError(f"Strip '{strip_name}' não encontrado para split.")

    frames = sorted(int(t * fps) for t in split_times)
    for f in reversed(frames):
        scene.frame_current = f
        bpy.ops.sequencer.select_all(action='DESELECT')
        strip.select = True
        bpy.ops.sequencer.split(frame=f, type='SOFT', side='LEFT')

    new_strips = [s.name for s in seqs if s.name.startswith(strip_name)]
    log.debug("Split em '%s' nos frames %s, gerou: %s", strip_name, frames, new_strips)
    return new_strips


def cut_video_strip(strip_name: str, start_time: float, end_time: float, fps: int) -> str:
    scene = ensure_editor()
    seqs = scene.sequence_editor.sequences_all
    orig = seqs.get(strip_name)
    if orig is None:
        raise ValueError(f"Strip '{strip_name}' não encontrado para cut.")

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
            log.debug("cut_video_strip: Removido '%s'", name)

    if middle:
        new_name = f"{strip_name}_cut"
        middle.name = new_name
        log.debug("cut_video_strip: Strip resultante '%s' (start=%s, end=%s)", new_name, start_time, end_time)
        return new_name
    raise RuntimeError(f"cut_video_strip: Não foi possível encontrar o trecho intermediário para '{strip_name}'.")


