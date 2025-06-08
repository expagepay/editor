# utils/audio_utils.py

import bpy
import os

def add_audio_strip(audio_path: str, channel: int = 1, frame_start: int = 1):
    """
    Adiciona um strip de áudio. Retorna o objeto de strip inserido.
    """
    scene = bpy.context.scene
    if not scene.sequence_editor:
        scene.sequence_editor_create()

    strip = scene.sequence_editor.sequences.new_sound(
        name=os.path.splitext(os.path.basename(audio_path))[0],
        filepath=audio_path,
        channel=channel,
        frame_start=frame_start
    )
    print(f"Áudio '{strip.name}' adicionado: start={strip.frame_final_start}, end={strip.frame_final_end}")
    return strip


def split_audio_strip(strip_name: str, split_times: list, fps: int) -> list:
    """
    Divide o strip de áudio identificado por 'strip_name' em vários trechos,
    sem remover conteúdo. split_times: lista de segundos.
    Retorna lista de nomes dos novos strips.
    """
    scene = bpy.context.scene
    seqs = scene.sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if strip is None:
        raise ValueError(f"Strip de áudio '{strip_name}' não encontrado para split.")

    frames = sorted(int(t * fps) for t in split_times)
    for f in reversed(frames):
        bpy.context.scene.frame_current = f
        bpy.ops.sequencer.select_all(action='DESELECT')
        strip.select = True
        bpy.ops.sequencer.split(frame=f, type='SOFT', side='LEFT')

    new_strips = [s.name for s in seqs if s.name.startswith(strip_name)]
    print(f"Split em áudio '{strip_name}' nos frames {frames}, gerou: {new_strips}")
    return new_strips


def cut_audio_strip(strip_name: str, start_time: float, end_time: float, fps: int) -> str:
    """
    Mantém apenas o trecho do strip de áudio entre start_time e end_time (em segundos).
    Remove antes de start_time e após end_time. Retorna o nome do strip resultante
    (renomeado para '<strip_name>_cut').
    """
    scene = bpy.context.scene
    seqs = scene.sequence_editor.sequences_all
    orig = seqs.get(strip_name)
    if orig is None:
        raise ValueError(f"Strip de áudio '{strip_name}' não encontrado para cut.")

    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)

    # 1) Split em end_frame
    bpy.context.scene.frame_current = end_frame
    bpy.ops.sequencer.select_all(action='DESELECT')
    orig.select = True
    bpy.ops.sequencer.split(frame=end_frame, type='SOFT', side='LEFT')
    seqs = scene.sequence_editor.sequences_all
    before_end = seqs.get(strip_name)  # trecho até end_frame
    after_end = next((s for s in seqs if s.name.startswith(strip_name + ".00") and s.frame_final_start > end_frame), None)

    # 2) Split em start_frame no trecho before_end
    bpy.context.scene.frame_current = start_frame
    bpy.ops.sequencer.select_all(action='DESELECT')
    before_end.select = True
    bpy.ops.sequencer.split(frame=start_frame, type='SOFT', side='LEFT')
    seqs = scene.sequence_editor.sequences_all
    before_start = seqs.get(strip_name)       # trecho antes de start
    middle = next((s for s in seqs if s.name.startswith(strip_name + ".00") and s.frame_final_end <= end_frame), None)
    after_middle = next((s for s in seqs if s.name.startswith(strip_name + ".00") and s.frame_final_start >= end_frame), None)

    # 3) Deleta before_start e after_end (se existir)
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

    # 4) Renomeia o trecho restante (middle) para '<strip_name>_cut'
    if middle:
        new_name = f"{strip_name}_cut"
        middle.name = new_name
        print(f"cut_audio_strip: Strip resultante '{new_name}' (start={start_time}s, end={end_time}s)")
        return new_name
    else:
        raise RuntimeError(f"cut_audio_strip: Não foi possível encontrar trecho intermediário para '{strip_name}'.")


def set_audio_volume(strip_name: str, volume_percent: float):
    """
    Ajusta o volume de um strip de áudio. volume_percent varia de 0 a 200
    (100 = original). O VSE usa 'volume' em 0.0–10.0, então convertemos.
    """
    seqs = bpy.context.scene.sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if strip is None:
        raise ValueError(f"Strip de áudio '{strip_name}' não encontrado para ajuste de volume.")

    # Converte 0–200% para 0.0–2.0
    vol = max(0.0, min(volume_percent / 100.0, 2.0))
    strip.volume = vol
    print(f"set_audio_volume: Strip '{strip_name}' volume ajustado para {volume_percent}% (valor Blender={vol})")


def extract_audio_from_video(video_strip_name: str, channel: int = 1, frame_start: int = 1) -> str:
    """
    Extrai o áudio embutido em um strip de vídeo e cria um novo strip de áudio
    que referencia o mesmo arquivo de vídeo (Blender reconhece a faixa de áudio).
    Retorna o nome do novo strip de áudio criado.
    """
    seqs = bpy.context.scene.sequence_editor.sequences_all
    vstrip = seqs.get(video_strip_name)
    if vstrip is None:
        raise ValueError(f"Strip de vídeo '{video_strip_name}' não encontrado para extrair áudio.")

    # O caminho original do arquivo de vídeo
    video_path = vstrip.filepath
    # Adiciona um strip de áudio usando o mesmo arquivo de vídeo
    bpy.context.scene.frame_current = vstrip.frame_start
    bpy.ops.sequencer.sound_strip_add(
        filepath=video_path,
        channel=channel,
        frame_start=vstrip.frame_start
    )
    new_audio = bpy.context.scene.sequence_editor.sequences_all[-1]
    new_name = f"{video_strip_name}_audio"
    new_audio.name = new_name
    print(f"extract_audio_from_video: '{new_name}' criado a partir de '{video_strip_name}'")
    return new_name
