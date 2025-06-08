import bpy

from .common import ensure_editor, log


def transform_strip(strip, translate=(0, 0), rotation=0.0):
    scene = ensure_editor()
    trans = scene.sequence_editor.sequences.new_effect(
        name=f"Transform_{strip.name}",
        type='TRANSFORM',
        channel=strip.channel + 1,
        frame_start=int(strip.frame_start),
        frame_end=int(strip.frame_final_end),
        seq1=strip
    )
    dx, dy = translate
    trans.translate_start_x = int(dx)
    trans.translate_start_y = int(dy)
    trans.rotation_start = float(rotation)
    log.debug("Aplicado transform em '%s': translate=%s rotation=%s", strip.name, translate, rotation)
    return trans


def rotate_strip(strip_name: str, angle_deg: float):
    scene = ensure_editor()
    seqs = scene.sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if not strip:
        raise ValueError(f"Strip '{strip_name}' não encontrado para rotacionar.")

    trans = scene.sequence_editor.sequences.new_effect(
        name=f"Rotate_{strip_name}",
        type='TRANSFORM',
        channel=strip.channel + 1,
        frame_start=int(strip.frame_start),
        frame_end=int(strip.frame_final_end),
        seq1=strip,
    )
    trans.rotation_start = angle_deg
    log.debug("Strip '%s' rotacionado em %s°", strip_name, angle_deg)
    return trans


def translate_strip(strip_name: str, dx: float, dy: float):
    scene = ensure_editor()
    seqs = scene.sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if not strip:
        raise ValueError(f"Strip '{strip_name}' não encontrado para translação.")

    trans = scene.sequence_editor.sequences.new_effect(
        name=f"Translate_{strip_name}",
        type='TRANSFORM',
        channel=strip.channel + 1,
        frame_start=int(strip.frame_start),
        frame_end=int(strip.frame_final_end),
        seq1=strip,
    )
    trans.translate_start_x = int(dx)
    trans.translate_start_y = int(dy)
    log.debug("Strip '%s' deslocado em (%s, %s)", strip_name, dx, dy)
    return trans
