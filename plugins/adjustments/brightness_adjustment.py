# plugins/adjustments/brightness_adjustment.py

from .base_adjustment import BaseAdjustment
import bpy

class BrightnessAdjustment(BaseAdjustment):
    name = "brightness_adjustment"

    def apply(self, seq, fps):
        """
        Ajusta o brilho de um strip entre start e end (em segundos).
        Usa efeito 'COLOR' do VSE para multiplicar o valor de luminância.
        """
        scene = bpy.context.scene
        strip = seq.get(self.strip_name)
        if strip is None:
            raise ValueError(f"Strip '{self.strip_name}' não encontrado.")

        start_frame = int(self.params.get("start", 0.0) * fps)
        end_frame = int(self.params.get("end", 0.0) * fps)
        brightness = self.params.get("level", 1.0)  # >1 aumenta brilho

        color_effect = scene.sequence_editor.sequences.new_effect(
            name="BrightnessEffect",
            type='COLOR',
            channel=strip.channel + 1,
            frame_start=strip.frame_start,
            frame_end=strip.frame_final_end,
            seq1=strip
        )

        # No VSE, color_multiply impacta canais de cor. Para brilho, podemos
        # multiplicar todos os canais igualmente.
        bpy.context.scene.frame_set(start_frame)
        color_effect.color_multiply = brightness
        color_effect.keyframe_insert(data_path="color_multiply", frame=start_frame)
        bpy.context.scene.frame_set(end_frame)
        color_effect.color_multiply = 1.0
        color_effect.keyframe_insert(data_path="color_multiply", frame=end_frame)
