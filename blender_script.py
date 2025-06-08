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

strips = []
current_end = 0.0
for asset in config.get("assets", []):
    rel_path = asset["path"]
    abs_path = os.path.join(script_dir, rel_path)
    media_type = asset.get("type", "video")
    ch = asset.get("channel", 1)
    start = asset.get("start", 0.0)
    end = asset.get("end")
    if ch == 1:
        length = end - start if end is not None else None
        start_sec = current_end
        end_sec = start_sec + length if length is not None else None
    else:
        start_sec = start
        end_sec = end
    strip = blender_core.add_media(abs_path, media_type, start_sec, end_sec, ch)
    strips.append(strip)
    if ch == 1:
        current_end = strip.frame_final_end / fps


output_rel = config.get("output_path", "output/final_edit.mp4")
output_abs = os.path.join(script_dir, output_rel)
res_x = config.get("resolution_x", 1920)
res_y = config.get("resolution_y", 1080)
scene = bpy.context.scene
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.audio_codec = 'AAC'
scene.render.ffmpeg.audio_bitrate = 192
scene.render.ffmpeg.audio_channels = 'STEREO'
blender_core.finalize_render(output_abs, res_x, res_y, fps)
