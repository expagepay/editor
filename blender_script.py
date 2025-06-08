# blender_script_template.py

import bpy
import json
import os
import sys

# 1. Garante importações corretas — define script_dir como base para caminhos relativos
script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(script_dir)

# 2. Carrega o JSON de configuração
config_path = os.path.join(script_dir, "config", "project_config.json")
with open(config_path, "r") as f:
    config = json.load(f)

# 3. Importa funções core
from blender_core import (
    init_sequence,
    add_video_strip,
    add_audio_strip,
    add_image_strip,
    split_strip,
    delete_strip,
    merge_strips,
    transform_strip,
    finalize_render
)

# 4. Importa funções novas de clip_utils e audio_utils
from utils.clip_utils import split_video_strip, cut_video_strip
from utils.audio_utils import (
    split_audio_strip,
    cut_audio_strip,
    set_audio_volume,
    extract_audio_from_video
)

# 5. Ajusta FPS e inicializa Sequencer
fps = config.get("fps", 24)
sequence_collection = init_sequence(fps)
if sequence_collection is None:
    raise RuntimeError("Falha em inicializar Sequencer (VSE).")

# 6. Carrega assets em múltiplas faixas, corrigindo caminhos relativos para absolutos
video_strips = {}
for vid in config.get("videos", []):
    rel_path = vid["path"]                  # ex: "assets/video1.mp4"
    abs_path = os.path.join(script_dir, rel_path)
    ch = vid.get("channel", 1)
    fs = vid.get("start_frame", 1)
    nm = vid.get("name")
    strip = add_video_strip(abs_path, channel=ch, frame_start=fs)
    strip.name = nm
    video_strips[nm] = strip

audio_strips = {}
for aud in config.get("audios", []):
    rel_path = aud["path"]
    abs_path = os.path.join(script_dir, rel_path)
    ch = aud.get("channel", 1)
    fs = aud.get("start_frame", 1)
    nm = aud.get("name")
    strip = add_audio_strip(abs_path, channel=ch, frame_start=fs)
    strip.name = nm
    audio_strips[nm] = strip

image_strips = {}
for img in config.get("images", []):
    rel_path = img["path"]
    abs_path = os.path.join(script_dir, rel_path)
    ch = img.get("channel", 5)
    fs = img.get("start_frame", 1)
    fe = img.get("frame_end", None)
    nm = img.get("name")
    strip = add_image_strip(abs_path, channel=ch, frame_start=fs, frame_end=fe)
    strip.name = nm
    image_strips[nm] = strip

# 7. Executa cada operação em ordem. Agora reconhece também "split" como alias de "split_video".
ops = config.get("operations", [])
for op in ops:
    kind = op["type"]

    # ─────────────────────── Vídeo: split_video ou alias "split" ───────────────────────
    if kind in ("split_video", "split"):
        target = op["target"]
        split_times = op.get("times", [])
        strip = video_strips.get(target)
        if not strip:
            print(f"❌ split_video: strip '{target}' não encontrado.")
            continue
        new_names = split_video_strip(target, split_times, fps)
        # Se quiser usar os novos sub-strips em operações posteriores,
        # você pode iterar new_names e adicioná-los em video_strips[...]

    elif kind in ("cut_video", "cut_video_strip"):
        target = op["target"]
        start_time = op.get("start", 0.0)
        end_time = op.get("end", 0.0)
        new_name = cut_video_strip(target, start_time, end_time, fps)
        # Atualiza dicionário para futuras referências
        video_strips[new_name] = bpy.context.scene.sequence_editor.sequences_all.get(new_name)

    # ─────────────────────── Áudio: split_audio ou alias "split" ───────────────────────
    elif kind in ("split_audio",):
        target = op["target"]
        split_times = op.get("times", [])
        strip = audio_strips.get(target)
        if not strip:
            print(f"❌ split_audio: strip '{target}' não encontrado.")
            continue
        new_names = split_audio_strip(target, split_times, fps)
        # Se necessário, atualize audio_strips com new_names[...]

    elif kind == "cut_audio":
        target = op["target"]
        start_time = op.get("start", 0.0)
        end_time = op.get("end", 0.0)
        new_name = cut_audio_strip(target, start_time, end_time, fps)
        audio_strips[new_name] = bpy.context.scene.sequence_editor.sequences_all.get(new_name)

    # ─────────────────────── Audio: set_volume ───────────────────────
    elif kind == "set_volume":
        target = op["target"]
        vol = op.get("volume", 100)  # 0–200%
        set_audio_volume(target, vol)

    # ─────────────────────── Vídeo→Áudio: extract_audio ───────────────────────
    elif kind == "extract_audio":
        target = op["target"]
        channel = op.get("channel", 1)
        strip = video_strips.get(target)
        if not strip:
            print(f"❌ extract_audio: strip de vídeo '{target}' não encontrado.")
            continue
        new_name = extract_audio_from_video(target, channel=channel, frame_start=strip.frame_start)
        audio_strips[new_name] = bpy.context.scene.sequence_editor.sequences_all.get(new_name)

    # ─────────────────────── Delete, Merge e Transform ───────────────────────
    elif kind == "delete":
        target = op["target"]
        delete_strip(target)

    elif kind == "merge":
        targets = op.get("targets", [])
        out_name = op.get("output_name", "MergedMeta")
        merge_strips(targets, output_name=out_name)

    elif kind == "transform":
        target = op["target"]
        dx, dy = op.get("translate", [0, 0])
        angle = op.get("rotate", 0.0)
        strip = (
            video_strips.get(target) or
            image_strips.get(target) or
            audio_strips.get(target)
        )
        if not strip:
            print(f"❌ transform: strip '{target}' não encontrado.")
            continue
        transform_strip(strip, translate=(dx, dy), rotation=angle)

    else:
        print(f"⚠️ Operação desconhecida: {kind}")

# 8. Renderiza tudo
output_rel = config.get("output_path", "output/final_edit.mp4")
output_abs = os.path.join(script_dir, output_rel)
res_x = config.get("resolution_x", 1920)
res_y = config.get("resolution_y", 1080)
finalize_render(output_abs, res_x, res_y, fps)
