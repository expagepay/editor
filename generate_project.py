# generate_project.py

import json
import os
import shutil

def generate_project_file(config: dict):
    """
    Recebe um dicionário `config` completo, salva em config/project_config.json,
    e copia o template para blender_script.py (substituindo se já existir).
    """
    # 1. Garante que a pasta 'config' exista
    os.makedirs("config", exist_ok=True)

    # 2. Grava JSON de configuração
    with open("config/project_config.json", "w") as f:
        json.dump(config, f, indent=2)

    # 3. Sobrescreve (ou cria) o blender_script.py
    shutil.copy("blender_script_template.py", "blender_script.py")

    print("✅ project_config.json atualizado.")
    print("✅ blender_script.py pronto para rodar.")
    print("→ Para renderizar, execute: ./run_blender.sh")

if __name__ == "__main__":
    # Exemplo simples usando o novo esquema de assets
    example_config = {
        "assets": [
            {"path": "assets/video1.mp4", "type": "video", "start": 0,  "end": 10, "channel": 1},
            {"path": "assets/video2.mp4", "type": "video", "start": 10, "end": 20, "channel": 1},
            {"path": "assets/overlay.mp4", "type": "video", "start": 5,  "end": 15, "channel": 2},
            {"path": "assets/music.mp3",  "type": "audio", "start": 0,  "end": 20, "channel": 3},
        ],
        "output_path": "output/final_edit.mp4",
        "resolution_x": 1920,
        "resolution_y": 1080,
        "fps": 24,
    }

    generate_project_file(example_config)
