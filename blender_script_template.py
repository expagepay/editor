# blender_script_template.py

import bpy
import json
import os
import sys
import logging

# 1. Garante que podemos importar blender_core e utils
script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(script_dir)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

# 2. Carrega configuração JSON
config_path = os.path.join(script_dir, "config", "project_config.json")
with open(config_path, "r") as f:
    config = json.load(f)

# 3. Importa funções core
import blender_core

# 4. Define FPS e inicializa a Sequencer
fps = config.get("fps", 24)
sequence_collection = blender_core.init_sequence(fps)
if sequence_collection is None:
    raise RuntimeError("Falha em inicializar a Sequencer (VSE).")

# 5. Carrega assets em múltiplas faixas, mas converte paths relativos em absolutos
video_strips = {}
for vid in config.get("videos", []):
    # Reconstrói um caminho absoluto baseado na pasta do script
    rel_path = vid["path"]             # ex: "assets/video.mp4"
    abs_path = os.path.join(script_dir, rel_path)
    ch = vid.get("channel", 1)
    start_sec = vid.get("start_sec")
    if start_sec is None:
        start_sec = vid.get("start_frame", 1) / fps
    end_sec = vid.get("end_sec")
    nm = vid.get("name")
    strip = blender_core.add_media(abs_path, channel=ch, start_sec=start_sec, end_sec=end_sec, fps=fps)
    strip.name = nm
    video_strips[nm] = strip

audio_strips = {}
for aud in config.get("audios", []):
    rel_path = aud["path"]             # ex: "assets/audio.mp3"
    abs_path = os.path.join(script_dir, rel_path)
    ch = aud.get("channel", 3)
    start_sec = aud.get("start_sec")
    if start_sec is None:
        start_sec = aud.get("start_frame", 1) / fps
    end_sec = aud.get("end_sec")
    nm = aud.get("name")
    strip = blender_core.add_media(abs_path, channel=ch, start_sec=start_sec, end_sec=end_sec, fps=fps)
    strip.name = nm
    audio_strips[nm] = strip

image_strips = {}
for img in config.get("images", []):
    rel_path = img["path"]             # ex: "assets/image.png"
    abs_path = os.path.join(script_dir, rel_path)
    ch = img.get("channel", 5)
    start_sec = img.get("start_sec")
    if start_sec is None:
        start_sec = img.get("start_frame", 1) / fps
    end_sec = img.get("end_sec")
    if end_sec is None:
        fe = img.get("frame_end")
        end_sec = fe / fps if fe is not None else None
    nm = img.get("name")
    strip = blender_core.add_media(abs_path, channel=ch, start_sec=start_sec, end_sec=end_sec, fps=fps)
    strip.name = nm
    image_strips[nm] = strip

# (… resto do código mantém-se igual …)

# 6. Executa cada operação na ordem definida em "operations"
ops = config.get("operations", [])
for op in ops:
    kind = op["type"]

    if kind == "split":
        target = op["target"]
        times = op.get("times", [])
        strip = video_strips.get(target) or image_strips.get(target) or audio_strips.get(target)
        if not strip:
            print(f"❌ Split: strip '{target}' não encontrado.")
            continue
        blender_core.split_at(target, times, fps)

    elif kind == "delete":
        blender_core.delete_strip(op["target"])

    elif kind == "merge":
        blender_core.merge_strips(op.get("targets", []), output_name=op.get("output_name", "MergedMeta"))

    elif kind == "transform":
        target = op["target"]
        dx, dy = op.get("translate", [0, 0])
        angle = op.get("rotate", 0.0)
        strip = video_strips.get(target) or image_strips.get(target) or audio_strips.get(target)
        if not strip:
            print(f"❌ Transform: strip '{target}' não encontrado.")
            continue
        blender_core.transform_strip(strip, translate=(dx, dy), rotation=angle)

    else:
        print(f"⚠️ Operação desconhecida: {kind}")

# 7. Renderiza tudo
output_rel = config.get("output_path", "output/final_edit.mp4")
output_abs = os.path.join(script_dir, output_rel)
res_x = config.get("resolution_x", 1920)
res_y = config.get("resolution_y", 1080)
blender_core.finalize_render(output_abs, res_x, res_y, fps)
