# plugins/adjustments/contrast_adjustment.py

from .base_adjustment import BaseAdjustment
import bpy

class ContrastAdjustment(BaseAdjustment):
    name = "contrast_adjustment"

    def apply(self, seq, fps):
        """
        Ajusta o contraste de uma strip usando nó de Compositor ou efeito VSE.
        Aqui, usamos um “RGB Curves” no Compositor como exemplo.
        """
        scene = bpy.context.scene
        scene.use_nodes = True
        tree = scene.node_tree
        links = tree.links

        # Geralmente, para contraste, é melhor usar nós no Compositor.
        # Flow: Render Layers → RGB Curves → Composite → File Output
        # Mas como estamos em VSE, faremos um truque simples: usamos o efeito 'CURVE_RGB'

        strip = seq.get(self.strip_name)
        if strip is None:
            raise ValueError(f"Strip '{self.strip_name}' não encontrado.")

        start_frame = int(self.params.get("start", 0.0) * fps)
        end_frame = int(self.params.get("end", 0.0) * fps)
        contrast_value = self.params.get("contrast", 1.0)  # >1 aumenta contraste

        # Cria efeito de curvas RGB
        curve = scene.sequence_editor.sequences.new_effect(
            name="ContrastCurve",
            type='CURVE_RGB',
            channel=strip.channel + 1,
            frame_start=strip.frame_start,
            frame_end=strip.frame_final_end,
            seq1=strip
        )
        # Ajusta as curvas RGB (no VSE, o CURVE_RGB não é tão personalizável quanto no compositor)
        # Mas podemos simular: se contrast_value > 1, “puxa” pontos da curva.
        # No exemplo abaixo, deixamos os valores fixos. Para curva dinâmica, teríamos que usar nós.

        curve.mapping.curves[3].points.new(0.5, contrast_value)  # O canal combinado (index 3)

        # Keyframes de contraste
        bpy.context.scene.frame_set(start_frame)
        curve.keyframe_insert(data_path="mapping.curves[3].points[1].location", frame=start_frame)
        bpy.context.scene.frame_set(end_frame)
        curve.mapping.curves[3].points[1].location = (0.5, 1.0)
        curve.keyframe_insert(data_path="mapping.curves[3].points[1].location", frame=end_frame)
