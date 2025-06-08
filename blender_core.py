# blender_core.py

import bpy
import os

OPERATIONS: dict[str, callable] = {}

def register(name: str):
    def _decorator(fn):
        OPERATIONS[name] = fn
        return fn
    return _decorator

def _ensure_editor():
    scene = bpy.context.scene
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    return scene

@register("init_sequence")
def init_sequence(fps):
    """
    Cria (ou reseta) a Sequencer (VSE) e já ajusta o FPS da cena.
    Retorna a coleção de strips (bpy.types.bpy_prop_collection).
    """
    scene = bpy.context.scene

    # Ajusta FPS antes de carregar qualquer strip
    scene.render.fps = fps

    # Se já existir Sequencer, apaga tudo
    if scene.sequence_editor:
        bpy.ops.sequencer.select_all(action='SELECT')
        bpy.ops.sequencer.delete()
    scene.sequence_editor_create()
    return scene.sequence_editor.sequences_all


@register("add_video_strip")
def add_video_strip(video_path, channel=1, frame_start=1):
    """
    Adiciona um clipe de vídeo usando new_movie e, em seguida, força o frame_final_end
    a partir da duração real do arquivo (obtida via bpy.data.movieclips.load).
    Retorna o objeto de strip inserido na timeline.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")

    scene = _ensure_editor()

    # 1) Cria o strip com new_movie
    strip = scene.sequence_editor.sequences.new_movie(
        name=os.path.splitext(os.path.basename(video_path))[0],
        filepath=video_path,
        channel=channel,
        frame_start=frame_start
    )

    # 2) Para forçar a duração correta, carrega o MovieClip apenas para ler metadados
    try:
        mc = bpy.data.movieclips.load(video_path)
        # 'frame_duration' é o número total de frames do clipe
        duration_frames = int(mc.frame_duration)
        # Ajusta a duração do strip no VSE:
        strip.frame_final_end = strip.frame_start + duration_frames
        # Limpa o MovieClip da memória
        bpy.data.movieclips.remove(mc)
    except Exception as e:
        # Se falhar ao carregar o MovieClip, deixa como estava
        print(f"⚠️ Não foi possível ajustar duração do vídeo '{video_path}': {e}")

    print(f"Adicionado vídeo '{strip.name}': start={strip.frame_final_start}, end={strip.frame_final_end}")
    return strip


@register("add_audio_strip")
def add_audio_strip(audio_path, channel=2, frame_start=1):
    """
    Adiciona uma faixa de áudio usando new_sound. Por ora, confiamos no VSE
    para ler a duração correta (se ele não fizer isso, podemos reencodar ou
    extrair a duração com outra ferramenta). Retorna o objeto de strip inserido.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Áudio não encontrado: {audio_path}")
    scene = _ensure_editor()

    strip = scene.sequence_editor.sequences.new_sound(
        name=os.path.splitext(os.path.basename(audio_path))[0],
        filepath=audio_path,
        channel=channel,
        frame_start=frame_start
    )

    # Teste rápido: se acabar muito curto, avisa no console
    if strip.frame_final_end - strip.frame_start <= 2:
        print(f"⚠️ Atenção: áudio '{strip.name}' tem duração parecendo curta: end={strip.frame_final_end}")

    print(f"Adicionado áudio '{strip.name}': start={strip.frame_final_start}, end={strip.frame_final_end}")
    return strip


@register("add_image_strip")
def add_image_strip(image_path, channel=3, frame_start=1, frame_end=None):
    """
    Adiciona um strip de imagem (imagem estática). Se frame_end não for fornecido,
    dura 100 quadros a partir de frame_start. Retorna o objeto de strip criado.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")
    scene = _ensure_editor()

    strip = scene.sequence_editor.sequences.new_image(
        name=os.path.splitext(os.path.basename(image_path))[0],
        filepath=image_path,
        channel=channel,
        frame_start=frame_start
    )
    if frame_end is not None:
        strip.frame_final_end = frame_end
    else:
        strip.frame_final_end = strip.frame_start + 100

    print(f"Adicionado imagem '{strip.name}': start={strip.frame_start}, end={strip.frame_final_end}")
    return strip


@register("split_strip")
def split_strip(strip, split_frame):
    """
    Divide o strip (vídeo, áudio ou imagem) em dois no split_frame.
    """
    _ensure_editor()
    bpy.ops.sequencer.select_all(action='DESELECT')
    strip.select = True
    bpy.context.scene.frame_current = split_frame
    bpy.ops.sequencer.split(frame=split_frame, type='SOFT', side='LEFT')
    print(f"Strip '{strip.name}' dividido em frame {split_frame}.")


@register("delete_strip")
def delete_strip(strip_name):
    """
    Deleta totalmente o strip cujo nome é strip_name.
    """
    seqs = _ensure_editor().sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if strip:
        bpy.ops.sequencer.select_all(action='DESELECT')
        strip.select = True
        bpy.ops.sequencer.delete()
        print(f"Strip '{strip_name}' deletado.")
    else:
        print(f"Strip '{strip_name}' não encontrado para deletar.")


@register("merge_strips")
def merge_strips(strip_names, output_name="MergedMeta"):
    """
    Agrupa (cria Meta Strip) a lista de strips cujo nome está em strip_names.
    Retorna o Meta strip criado.
    """
    seqs = _ensure_editor().sequence_editor.sequences_all
    bpy.ops.sequencer.select_all(action='DESELECT')
    for name in strip_names:
        s = seqs.get(name)
        if s:
            s.select = True
    bpy.ops.sequencer.meta_make()
    meta = [s for s in seqs if s.type == 'META' and s.name.startswith("Meta")][0]
    meta.name = output_name
    print(f"Meta Strip '{output_name}' criado com: {strip_names}")
    return meta


@register("transform_strip")
def transform_strip(strip, translate=(0, 0), rotation=0.0):
    """
    Aplica transformações básicas a um strip:
      - translate: (dx, dy) em pixels
      - rotation: em graus
    Isso é feito criando um Effect Strip 'TRANSFORM' que recebe o strip original.
    """
    scene = _ensure_editor()
    trans = scene.sequence_editor.sequences.new_effect(
        name=f"Transform_{strip.name}",
        type='TRANSFORM',
        channel=strip.channel + 1,
        frame_start=strip.frame_start,
        frame_end=strip.frame_final_end,
        seq1=strip
    )
    dx, dy = translate
    trans.translate_start_x = int(dx)
    trans.translate_start_y = int(dy)
    trans.rotation_start = float(rotation)
    print(f"Aplicado transform em '{strip.name}': translate={translate}, rotation={rotation}°")
    return trans


@register("finalize_render")
def finalize_render(output_path, res_x, res_y, fps):
    """
    Configura todas as propriedades de render e dispara a renderização em modo
    ‘sequencer → compositor’.
    """
    import os
    scene = _ensure_editor()

    # 1. Resolução e FPS
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.fps = fps

    # 2. Caminho absoluto de saída
    if not output_path.lower().endswith(".mp4"):
        output_path = os.path.join(output_path, "output.mp4")
    output_path = os.path.abspath(output_path)
    scene.render.filepath = output_path

    # 3. Formato FFmpeg H.264 + AAC
    scene.render.use_sequencer = True
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.audio_codec = 'AAC'
    scene.render.ffmpeg.video_bitrate = 8000
    scene.render.ffmpeg.audio_bitrate = 192

    # 4. Ajusta frame_end baseado nos strips carregados
    seqs = scene.sequence_editor.sequences_all
    if seqs:
        scene.frame_start = 1
        scene.frame_end = max([s.frame_final_end for s in seqs])
        print(f"🔢 Range de frames: {scene.frame_start} → {scene.frame_end}")
    else:
        scene.frame_start = 1
        scene.frame_end = 100
        print("⚠️ Nenhum strip encontrado, usando 100 frames de fallback.")

    print("Renderizando para:", output_path)
    bpy.ops.render.render(animation=True)

    if os.path.exists(output_path):
        print("✅ Render concluído:", output_path)
    else:
        print("❌ Falha no render: arquivo não foi criado.")


@register("split_video_strip")
def split_video_strip(strip_name: str, split_times: list, fps: int) -> list:
    scene = _ensure_editor()
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
    print(f"Split em '{strip_name}' nos frames {frames}, gerou: {new_strips}")
    return new_strips


@register("cut_video_strip")
def cut_video_strip(strip_name: str, start_time: float, end_time: float, fps: int) -> str:
    scene = _ensure_editor()
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
            print(f"cut_video_strip: Removido '{name}'")

    if middle:
        new_name = f"{strip_name}_cut"
        middle.name = new_name
        print(f"cut_video_strip: Strip resultante '{new_name}' (start={start_time}s, end={end_time}s)")
        return new_name
    else:
        raise RuntimeError(f"cut_video_strip: Não foi possível encontrar o trecho intermediário para '{strip_name}'.")


@register("split_audio_strip")
def split_audio_strip(strip_name: str, split_times: list, fps: int) -> list:
    scene = _ensure_editor()
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
    print(f"Split em áudio '{strip_name}' nos frames {frames}, gerou: {new_strips}")
    return new_strips


@register("cut_audio_strip")
def cut_audio_strip(strip_name: str, start_time: float, end_time: float, fps: int) -> str:
    scene = _ensure_editor()
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
            print(f"cut_audio_strip: Removido '{name}'")

    if middle:
        new_name = f"{strip_name}_cut"
        middle.name = new_name
        print(f"cut_audio_strip: Strip resultante '{new_name}' (start={start_time}s, end={end_time}s)")
        return new_name
    else:
        raise RuntimeError(f"cut_audio_strip: Não foi possível encontrar trecho intermediário para '{strip_name}'.")


@register("set_audio_volume")
def set_audio_volume(strip_name: str, volume_percent: float):
    seqs = _ensure_editor().sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if strip is None:
        raise ValueError(f"Strip de áudio '{strip_name}' não encontrado para ajuste de volume.")

    vol = max(0.0, min(volume_percent / 100.0, 2.0))
    strip.volume = vol
    print(f"set_audio_volume: Strip '{strip_name}' volume ajustado para {volume_percent}% (valor Blender={vol})")


@register("extract_audio_from_video")
def extract_audio_from_video(video_strip_name: str, channel: int = 1, frame_start: int = 1) -> str:
    seqs = _ensure_editor().sequence_editor.sequences_all
    vstrip = seqs.get(video_strip_name)
    if vstrip is None:
        raise ValueError(f"Strip de vídeo '{video_strip_name}' não encontrado para extrair áudio.")

    video_path = vstrip.filepath
    scene = bpy.context.scene
    scene.frame_current = vstrip.frame_start
    bpy.ops.sequencer.sound_strip_add(
        filepath=video_path,
        channel=channel,
        frame_start=vstrip.frame_start,
    )
    new_audio = scene.sequence_editor.sequences_all[-1]
    new_name = f"{video_strip_name}_audio"
    new_audio.name = new_name
    print(f"extract_audio_from_video: '{new_name}' criado a partir de '{video_strip_name}'")
    return new_name


@register("rotate_strip")
def rotate_strip(strip_name: str, angle_deg: float):
    scene = _ensure_editor()
    seqs = scene.sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if not strip:
        raise ValueError(f"Strip '{strip_name}' não encontrado para rotacionar.")

    trans = scene.sequence_editor.sequences.new_effect(
        name=f"Rotate_{strip_name}",
        type='TRANSFORM',
        channel=strip.channel + 1,
        frame_start=strip.frame_start,
        frame_end=strip.frame_final_end,
        seq1=strip,
    )
    trans.rotation_start = angle_deg
    print(f"Strip '{strip_name}' rotacionado em {angle_deg}°")
    return trans


@register("translate_strip")
def translate_strip(strip_name: str, dx: float, dy: float):
    scene = _ensure_editor()
    seqs = scene.sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if not strip:
        raise ValueError(f"Strip '{strip_name}' não encontrado para translação.")

    trans = scene.sequence_editor.sequences.new_effect(
        name=f"Translate_{strip_name}",
        type='TRANSFORM',
        channel=strip.channel + 1,
        frame_start=strip.frame_start,
        frame_end=strip.frame_final_end,
        seq1=strip,
    )
    trans.translate_start_x = int(dx)
    trans.translate_start_y = int(dy)
    print(f"Strip '{strip_name}' deslocado em ({dx}, {dy})")
    return trans

__all__ = list(OPERATIONS.keys())

