# blender_core.py

import bpy
import os

def init_sequence(fps):
    """
    Cria (ou reseta) a Sequencer (VSE) e já ajusta o FPS da cena.
    Retorna a coleção de strips (bpy.types.bpy_prop_collection).
    """
    scene = bpy.context.scene

    # Ajusta FPS antes de carregar qualquer strip
    scene.render.fps = fps

    # Se já existir Sequencer, apaga tudo
    if scene.sequence_editor:
        bpy.ops.sequencer.select_all(action='SELECT')
        bpy.ops.sequencer.delete()
    scene.sequence_editor_create()
    return scene.sequence_editor.sequences_all


def add_video_strip(video_path, channel=1, frame_start=1):
    """
    Adiciona um clipe de vídeo usando new_movie e, em seguida, força o frame_final_end
    a partir da duração real do arquivo (obtinada via bpy.data.movieclips.load).
    Retorna o objeto de strip inserido na timeline.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")

    scene = bpy.context.scene
    if not scene.sequence_editor:
        scene.sequence_editor_create()

    # 1) Cria o strip com new_movie
    strip = scene.sequence_editor.sequences.new_movie(
        name=os.path.splitext(os.path.basename(video_path))[0],
        filepath=video_path,
        channel=channel,
        frame_start=frame_start
    )

    # 2) Para forçar a duração correta, carrega o MovieClip apenas para ler metadados
    try:
        mc = bpy.data.movieclips.load(video_path)
        # 'frame_duration' é o número total de frames do clipe
        duration_frames = int(mc.frame_duration)
        # Ajusta a duração do strip no VSE:
        strip.frame_final_end = strip.frame_start + duration_frames
        # Limpa o MovieClip da memória
        bpy.data.movieclips.remove(mc)
    except Exception as e:
        # Se falhar ao carregar o MovieClip, deixa como estava
        print(f"⚠️ Não foi possível ajustar duração do vídeo '{video_path}': {e}")

    print(f"Adicionado vídeo '{strip.name}': start={strip.frame_final_start}, end={strip.frame_final_end}")
    return strip


def add_audio_strip(audio_path, channel=2, frame_start=1):
    """
    Adiciona uma faixa de áudio usando new_sound. Por ora, confiamos no VSE
    para ler a duração correta (se ele não fizer isso, podemos reencodar ou
    extrair a duração com outra ferramenta). Retorna o objeto de strip inserido.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Áudio não encontrado: {audio_path}")
    scene = bpy.context.scene
    if not scene.sequence_editor:
        scene.sequence_editor_create()

    strip = scene.sequence_editor.sequences.new_sound(
        name=os.path.splitext(os.path.basename(audio_path))[0],
        filepath=audio_path,
        channel=channel,
        frame_start=frame_start
    )

    # Teste rápido: se acabar muito curto, avisa no console
    if strip.frame_final_end - strip.frame_start <= 2:
        print(f"⚠️ Atenção: áudio '{strip.name}' tem duração parecendo curta: end={strip.frame_final_end}")

    print(f"Adicionado áudio '{strip.name}': start={strip.frame_final_start}, end={strip.frame_final_end}")
    return strip


def add_image_strip(image_path, channel=3, frame_start=1, frame_end=None):
    """
    Adiciona um strip de imagem (imagem estática). Se frame_end não for fornecido,
    dura 100 quadros a partir de frame_start. Retorna o objeto de strip criado.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")
    scene = bpy.context.scene
    if not scene.sequence_editor:
        scene.sequence_editor_create()

    strip = scene.sequence_editor.sequences.new_image(
        name=os.path.splitext(os.path.basename(image_path))[0],
        filepath=image_path,
        channel=channel,
        frame_start=frame_start
    )
    if frame_end is not None:
        strip.frame_final_end = frame_end
    else:
        strip.frame_final_end = strip.frame_start + 100

    print(f"Adicionado imagem '{strip.name}': start={strip.frame_start}, end={strip.frame_final_end}")
    return strip


def split_strip(strip, split_frame):
    """
    Divide o strip (vídeo, áudio ou imagem) em dois no split_frame.
    """
    bpy.ops.sequencer.select_all(action='DESELECT')
    strip.select = True
    bpy.context.scene.frame_current = split_frame
    bpy.ops.sequencer.split(frame=split_frame, type='SOFT', side='LEFT')
    print(f"Strip '{strip.name}' dividido em frame {split_frame}.")


def delete_strip(strip_name):
    """
    Deleta totalmente o strip cujo nome é strip_name.
    """
    seqs = bpy.context.scene.sequence_editor.sequences_all
    strip = seqs.get(strip_name)
    if strip:
        bpy.ops.sequencer.select_all(action='DESELECT')
        strip.select = True
        bpy.ops.sequencer.delete()
        print(f"Strip '{strip_name}' deletado.")
    else:
        print(f"Strip '{strip_name}' não encontrado para deletar.")


def merge_strips(strip_names, output_name="MergedMeta"):
    """
    Agrupa (cria Meta Strip) a lista de strips cujo nome está em strip_names.
    Retorna o Meta strip criado.
    """
    seqs = bpy.context.scene.sequence_editor.sequences_all
    bpy.ops.sequencer.select_all(action='DESELECT')
    for name in strip_names:
        s = seqs.get(name)
        if s:
            s.select = True
    bpy.ops.sequencer.meta_make()
    meta = [s for s in seqs if s.type == 'META' and s.name.startswith("Meta")][0]
    meta.name = output_name
    print(f"Meta Strip '{output_name}' criado com: {strip_names}")
    return meta


def transform_strip(strip, translate=(0, 0), rotation=0.0):
    """
    Aplica transformações básicas a um strip:
      - translate: (dx, dy) em pixels
      - rotation: em graus
    Isso é feito criando um Effect Strip 'TRANSFORM' que recebe o strip original.
    """
    scene = bpy.context.scene
    trans = scene.sequence_editor.sequences.new_effect(
        name=f"Transform_{strip.name}",
        type='TRANSFORM',
        channel=strip.channel + 1,
        frame_start=strip.frame_start,
        frame_end=strip.frame_final_end,
        seq1=strip
    )
    dx, dy = translate
    trans.translate_start_x = int(dx)
    trans.translate_start_y = int(dy)
    trans.rotation_start = float(rotation)
    print(f"Aplicado transform em '{strip.name}': translate={translate}, rotation={rotation}°")
    return trans


def finalize_render(output_path, res_x, res_y, fps):
    """
    Configura todas as propriedades de render e dispara a renderização em modo
    ‘sequencer → compositor’.
    """
    import os
    scene = bpy.context.scene

    # 1. Resolução e FPS
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.fps = fps

    # 2. Caminho absoluto de saída
    if not output_path.lower().endswith(".mp4"):
        output_path = os.path.join(output_path, "output.mp4")
    output_path = os.path.abspath(output_path)
    scene.render.filepath = output_path

    # 3. Formato FFmpeg H.264 + AAC
    scene.render.use_sequencer = True
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.audio_codec = 'AAC'
    scene.render.ffmpeg.video_bitrate = 8000
    scene.render.ffmpeg.audio_bitrate = 192

    # 4. Ajusta frame_end baseado nos strips carregados
    seqs = scene.sequence_editor.sequences_all
    if seqs:
        scene.frame_start = 1
        scene.frame_end = max([s.frame_final_end for s in seqs])
        print(f"🔢 Range de frames: {scene.frame_start} → {scene.frame_end}")
    else:
        scene.frame_start = 1
        scene.frame_end = 100
        print("⚠️ Nenhum strip encontrado, usando 100 frames de fallback.")

    print("Renderizando para:", output_path)
    bpy.ops.render.render(animation=True)

    if os.path.exists(output_path):
        print("✅ Render concluído:", output_path)
    else:
        print("❌ Falha no render: arquivo não foi criado.")
