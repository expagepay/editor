# utils/clip_utils.py

import bpy

def split_video_strip(strip_name: str, split_times: list, fps: int) -> list:
    """
    Divide o strip de vídeo identificado por 'strip_name' em vários trechos,
    sem remover nenhum pedaço. split_times é uma lista de tempos (em segundos)
    onde se quer dividir. Retorna a lista de nomes dos novos strips gerados.

    Exemplo de uso:
        split_video_strip("video1", [2.0, 5.0], 24)
    """
    scene = bpy.context.scene
    seqs = scene.sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if strip is None:
        raise ValueError(f"Strip '{strip_name}' não encontrado para split.")

    # Converte cada tempo em frame e ordena
    frames = sorted(int(t * fps) for t in split_times)
    # Divide em ordem reversa de frames, para não bagunçar índices
    for f in reversed(frames):
        bpy.context.scene.frame_current = f
        bpy.ops.sequencer.select_all(action='DESELECT')
        strip.select = True
        bpy.ops.sequencer.split(frame=f, type='SOFT', side='LEFT')

    # Depois de dividir, retorna todos os strips que começam com strip_name
    new_strips = [s.name for s in seqs if s.name.startswith(strip_name)]
    print(f"Split em '{strip_name}' nos frames {frames}, gerou: {new_strips}")
    return new_strips


def cut_video_strip(strip_name: str, start_time: float, end_time: float, fps: int) -> str:
    """
    Mantém apenas o trecho do strip de vídeo entre start_time e end_time (ambos em segundos).
    Todo conteúdo fora desse intervalo é deletado.
    Retorna o nome do strip resultante (“original” ou sub‐strip) que permanece na timeline,
    renomeado como '<strip_name>_cut' (para evitar colisões).
    
    Lógica:
      1. Converte start/end em frames.
      2. Divide o strip em 3 pedaços (antes de start, entre start/end, após end).
      3. Remove o pedaço antes de start e o pedaço após end.
      4. Renomeia o trecho restante para '<strip_name>_cut'.
    """
    scene = bpy.context.scene
    seqs = scene.sequence_editor.sequences_all
    orig = seqs.get(strip_name)
    if orig is None:
        raise ValueError(f"Strip '{strip_name}' não encontrado para cut.")

    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)

    # 1) Separa em dois em end_frame (gera orig e orig.001)
    bpy.context.scene.frame_current = end_frame
    bpy.ops.sequencer.select_all(action='DESELECT')
    orig.select = True
    bpy.ops.sequencer.split(frame=end_frame, type='SOFT', side='LEFT')
    # Agora há dois strips: orig (do início até end_frame) e orig.001 (o que sobra após end_frame)
    seqs = scene.sequence_editor.sequences_all
    # Re-obter referência ao trecho “antes de end”
    first_part = seqs.get(strip_name)
    second_part = next((s for s in seqs if s.name.startswith(strip_name + ".00")), None)

    # 2) Divide o primeiro_part em start_frame (gera 3 pedaços: antes do start, entre start/end, e após (depois de end, mas removido já))
    bpy.context.scene.frame_current = start_frame
    bpy.ops.sequencer.select_all(action='DESELECT')
    first_part.select = True
    bpy.ops.sequencer.split(frame=start_frame, type='SOFT', side='LEFT')
    # Agora, existem: 
    #   - orig (frame_start → start_frame)
    #   - orig.001 (start_frame → end_frame)
    #   - orig.002 (end_frame → final) — mas cuidado: orig.002 pode não existir, pois orig.002 poderia ter sido “first_part” após o split, precisamos identificar
    seqs = scene.sequence_editor.sequences_all
    before_strip = seqs.get(strip_name)                      # trecho antes de start_time
    middle_strip = next((s for s in seqs if s.name.startswith(strip_name + ".00") and s.frame_final_end <= end_frame), None)
    after_strip = next((s for s in seqs if s.name.startswith(strip_name + ".00") and s.frame_final_start >= end_frame), None)

    # 3) Deleta before_strip e second_part (o pedaço após end) e after_strip, se existirem
    to_delete = []
    if before_strip:
        to_delete.append(before_strip.name)
    if second_part:
        to_delete.append(second_part.name)
    if after_strip and after_strip.name not in to_delete:
        to_delete.append(after_strip.name)

    for name in to_delete:
        strip_to_del = seqs.get(name)
        if strip_to_del:
            bpy.ops.sequencer.select_all(action='DESELECT')
            strip_to_del.select = True
            bpy.ops.sequencer.delete()
            print(f"cut_video_strip: Removido '{name}'")

    # 4) Resta apenas o middle_strip: renomeia para '<strip_name>_cut'
    if middle_strip:
        new_name = f"{strip_name}_cut"
        middle_strip.name = new_name
        print(f"cut_video_strip: Strip resultante '{new_name}' (start={start_time}s, end={end_time}s)")
        return new_name
    else:
        raise RuntimeError(f"cut_video_strip: Não foi possível encontrar o trecho intermediário para '{strip_name}'.")


# Atenção: a função split_video_strip permanece sem alterações,
# apenas movemos ela para cá, caso você queira manter a divisão sem excluir nada.
