# plugins/adjustments/saturation_adjustment.py

from .base_adjustment import BaseAdjustment
import bpy

class SaturationAdjustment(BaseAdjustment):
    name = "saturation_adjustment"

    def apply(self, seq, fps):
        """
        Aplica ajuste de saturação a um strip entre start e end.
        Usa um nó de Compositor no Blender.
        """
        scene = bpy.context.scene
        # Habilita o uso do Compositor
        scene.use_nodes = True
        tree = scene.node_tree
        links = tree.links

        # Carrega o strip para renderizar como imagem de entrada no compositor
        # Usando o “Render Layers” ou “Image Input” não serve para VSE diretamente.
        # Estratégia: usar o VSE → Composite, depois reusar Composite para gravação.
        # Para simplificar neste exemplo, ajustamos diretamente Properties de cor do strip.

        strip = seq.get(self.strip_name)
        if strip is None:
            raise ValueError(f"Strip '{self.strip_name}' não encontrado.")

        # Obtém frames de início e fim (em frame count)
        start_frame = int(self.params.get("start", 0.0) * fps)
        end_frame = int(self.params.get("end", 0.0) * fps)
        intensity = self.params.get("level", 1.0)  # 1.0 = sem mudança

        # Cria um efeito de cor LUT para saturação no VSE
        color_effect = scene.sequence_editor.sequences.new_effect(
            name="SaturationEffect",
            type='COLOR',
            channel=strip.channel + 1,
            frame_start=strip.frame_start,
            frame_end=strip.frame_final_end,
            seq1=strip
        )
        # Ajusta saturação via propriedade do efeito (sempre entre 0.0 e 2.0, onde 1.0 = normal)
        # No VSE, o efeito 'COLOR' expõe dois valores: color_multiply e rgb curves,
        # mas o usuário pode fazer ajustes mais avançados no compositor.
        color_effect.color_multiply = intensity  # multiplicador simples no canal
        # Se quiser keyframes de saturação ao longo do tempo:
        bpy.context.scene.frame_set(start_frame)
        color_effect.keyframe_insert(data_path="color_multiply", frame=start_frame)
        bpy.context.scene.frame_set(end_frame)
        color_effect.color_multiply = 1.0  # volta à saturação normal
        color_effect.keyframe_insert(data_path="color_multiply", frame=end_frame)
