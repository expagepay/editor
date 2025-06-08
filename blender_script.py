import bpy
import json
import os
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(script_dir)

config_path = os.path.join(script_dir, "config", "project_config.json")
with open(config_path, "r") as f:
    config = json.load(f)

import blender_core

fps = config.get("fps", 24)
sequence_collection = blender_core.init_sequence(fps)
if sequence_collection is None:
    raise RuntimeError("Falha em inicializar Sequencer (VSE).")

video_strips = {}
current_end = 0
for vid in config.get("videos", []):
    rel_path = vid["path"]
    abs_path = os.path.join(script_dir, rel_path)
    ch = vid.get("channel", 1)
    start_sec = vid.get("start_sec")
    if start_sec is None:
        start_sec = vid.get("start_frame", 1) / fps
    end_sec = vid.get("end_sec")
    name = vid.get("name")
    if ch == 1:
        start_sec = current_end / fps
    strip = blender_core.add_media(abs_path, channel=ch, start_sec=start_sec, end_sec=end_sec, fps=fps)
    strip.name = name
    video_strips[name] = strip
    if ch == 1:
        current_end = strip.frame_final_end

audio_strips = {}
for aud in config.get("audios", []):
    rel_path = aud["path"]
    abs_path = os.path.join(script_dir, rel_path)
    ch = aud.get("channel", 1)
    start_sec = aud.get("start_sec")
    if start_sec is None:
        start_sec = aud.get("start_frame", 1) / fps
    end_sec = aud.get("end_sec")
    name = aud.get("name")
    strip = blender_core.add_media(abs_path, channel=ch, start_sec=start_sec, end_sec=end_sec, fps=fps)
    strip.name = name
    audio_strips[name] = strip

image_strips = {}
for img in config.get("images", []):
    rel_path = img["path"]
    abs_path = os.path.join(script_dir, rel_path)
    ch = img.get("channel", 5)
    start_sec = img.get("start_sec")
    if start_sec is None:
        start_sec = img.get("start_frame", 1) / fps
    end_sec = img.get("end_sec")
    if end_sec is None:
        fe = img.get("frame_end")
        end_sec = fe / fps if fe is not None else None
    name = img.get("name")
    strip = blender_core.add_media(abs_path, channel=ch, start_sec=start_sec, end_sec=end_sec, fps=fps)
    strip.name = name
    image_strips[name] = strip

ops = config.get("operations", [])
for op in ops:
    kind = op["type"]

    if kind == "split":
        blender_core.split_at(op["target"], op.get("times", []), fps)

    elif kind == "cut":
        blender_core.cut_between(op["target"], op.get("start", 0.0), op.get("end", 0.0), fps)

    elif kind == "set_volume":
        blender_core.set_audio_volume(op["target"], op.get("volume", 100))

    elif kind == "extract_audio":
        target = op["target"]
        channel = op.get("channel", 1)
        strip = video_strips.get(target)
        if not strip:
            print(f"❌ extract_audio: strip de vídeo '{target}' não encontrado.")
            continue
        new_name = blender_core.extract_audio_from_video(target, channel=channel, frame_start=strip.frame_start)
        audio_strips[new_name] = bpy.context.scene.sequence_editor.sequences_all.get(new_name)

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
            print(f"❌ transform: strip '{target}' não encontrado.")
            continue
        blender_core.transform_strip(strip, translate=(dx, dy), rotation=angle)

    else:
        print(f"⚠️ Operação desconhecida: {kind}")

output_rel = config.get("output_path", "output/final_edit.mp4")
output_abs = os.path.join(script_dir, output_rel)
res_x = config.get("resolution_x", 1920)
res_y = config.get("resolution_y", 1080)
blender_core.finalize_render(output_abs, res_x, res_y, fps)
