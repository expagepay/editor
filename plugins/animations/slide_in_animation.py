# plugins/animations/slide_in_animation.py

from .base_animation import BaseAnimation
import bpy

class SlideInAnimation(BaseAnimation):
    name = "slide_in_animation"

    def apply(self, seq, fps):
        """
        Faz um strip (por ex., imagem ou texto) deslizar da esquerda para o centro
        entre start_time e end_time.
        """
        scene = bpy.context.scene
        strip = seq.get(self.strip_name)
        if strip is None:
            raise ValueError(f"Strip '{self.strip_name}' não encontrado.")

        start_frame = int(self.start_time * fps)
        end_frame = int(self.end_time * fps)

        # Supondo uma resolução padrão 1920x1080, o centro (0,0) é 0,0 em transform
        # No VSE, o Transform effect manipula offset de posição.
        trans = scene.sequence_editor.sequences.new_effect(
            name="SlideInTransform",
            type='TRANSFORM',
            channel=strip.channel + 1,
            frame_start=strip.frame_start,
            frame_end=strip.frame_final_end,
            seq1=strip
        )

        # Posição inicial (fora da tela à esquerda): supondo -1.0 (relativo),
        # Mas no VSE, translate X é em pixels; vamos usar metade da largura
        width = scene.render.resolution_x
        off_start = -width
        off_end = 0

        # Keyframe início
        bpy.context.scene.frame_set(start_frame)
        trans.translate_start_x = off_start
        trans.keyframe_insert(data_path="translate_start_x", frame=start_frame)

        # Keyframe final
        bpy.context.scene.frame_set(end_frame)
        trans.translate_start_x = off_end
        trans.keyframe_insert(data_path="translate_start_x", frame=end_frame)
