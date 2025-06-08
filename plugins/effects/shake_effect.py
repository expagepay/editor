# effects/shake_effect.py

from .base_effect import BaseEffect

class ShakeEffect(BaseEffect):
    name = "shake"

    def apply(self, seq, audio_seq, fps):
        """
        Implementa um shake no vídeo entre start_time e end_time.
        O shake pode ser feito animando a câmera ou aplicando um efeito ‘transform’ com keyframes.
        Para simplicidade, vamos criar um Transform effect strip que modula a posição.
        """
        import bpy
        from random import uniform

        start_frame = int(self.start_time * fps)
        end_frame = int(self.end_time * fps)

        video_strip = seq
        print(video_strip)
        # Criar um efeito de transformação na mesma faixa de canal + 1
        trans = bpy.context.scene.sequence_editor.sequences.new_effect(
            name="ShakeTransform",
            type='TRANSFORM',
            channel=video_strip.channel + 1,
            frame_start=int(video_strip.frame_start),
            frame_end=int(video_strip.frame_final_end),
            seq1=video_strip
        )
        # Adiciona keyframes para deslocar a strip levemente em X e Y, frame a frame
        for frame in range(start_frame, end_frame + 1):
            bpy.context.scene.frame_set(frame)
            # deslocamento randômico em pixels (ajuste amplitude em params)
            amp = self.params.get("amplitude", 10)
            dx = uniform(-amp, amp)
            dy = uniform(-amp, amp)
            trans.translate_start_x = dx
            trans.translate_start_y = dy
            trans.keyframe_insert(data_path="translate_start_x", frame=frame)
            trans.keyframe_insert(data_path="translate_start_y", frame=frame)
