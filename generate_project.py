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
    # Exemplo de um config inicial (você pode editar ou gerar dinamicamente via IA):
    example_config = {
        # 1. Lista de vídeos
        "videos": [
            {
                "path": "assets/video.mp4",
                "channel": 1,
                "start_frame": 1,
                "name": "video1"
            }
        ],
        # 2. Lista de áudios
        "audios": [
            {
                "path": "assets/audio.mp3",
                "channel": 3,
                "start_frame": 1,
                "name": "audio1"
            }
        ],
        "images": [
            {
            "path": "assets\image.png",
            "channel": 5,
            "start_frame": 1,
            "frame_end": 120,
            "name": "img1"
            }
        ],
        # 3. Lista de imagens
        # 4. Configurações de render
        "output_path": "output/final_edit.mp4",
        "resolution_x": 1920,
        "resolution_y": 1080,
        "fps": 24,

        # 5. Operações (em ordem) para cortar, deletar, mesclar, transformar, etc.
        "operations": [
            {
                "type": "cut_video_strip",
                "target": "video1",
                "times": [3.0, 5.0]
            },
            {
                "type": "delete",
                "target": "video1.001"
            },
            {
                "type": "transform",
                "target": "img1",
                "translate": [100, 50],
                "rotate": 15.0
            },
        ]
    }

    generate_project_file(example_config)
