# plugins/animations/base_animation.py

class BaseAnimation:
    """
    Interface para animações de clipes (slide in/out, fade geral, etc.).
    Cada animação atuará sobre um objeto (strip de vídeo ou texto) criando keyframes.
    """
    name = "base_animation"

    def __init__(self, strip_name: str, start_time: float, end_time: float, params: dict):
        """
        strip_name: nome da strip a ser animada.
        start_time, end_time: período da animação em segundos.
        params: 
          - parâmetros específicos (direção, velocidade, etc.).
        """
        self.strip_name = strip_name
        self.start_time = start_time
        self.end_time = end_time
        self.params = params

    def apply(self, seq, fps):
        raise NotImplementedError("Cada animação deve implementar apply()")
