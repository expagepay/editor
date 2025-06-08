# utils/transform_utils.py

import bpy

def rotate_strip(strip_name: str, angle_deg: float):
    """
    Roda globalmente um strip (cria um efeito TRANSFORM) com ângulo em graus.
    """
    scene = bpy.context.scene
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
        seq1=strip
    )
    trans.rotation_start = angle_deg
    print(f"Strip '{strip_name}' rotacionado em {angle_deg}°")
    return trans


def translate_strip(strip_name: str, dx: float, dy: float):
    """
    Desloca um strip na tela (cria um efeito TRANSFORM) com deslocamento (dx, dy) em pixels.
    """
    scene = bpy.context.scene
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
        seq1=strip
    )
    trans.translate_start_x = int(dx)
    trans.translate_start_y = int(dy)
    print(f"Strip '{strip_name}' deslocado em ({dx}, {dy})")
    return trans
