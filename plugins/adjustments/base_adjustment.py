# plugins/adjustments/base_adjustment.py

class BaseAdjustment:
    """
    Interface para ajustes de vídeo (saturação, contraste, brilho etc.).
    Cada ajuste atua sobre um strip específico durante um período.
    """
    name = "base_adjustment"

    def __init__(self, strip_name: str, params: dict):
        """
        strip_name: nome da strip que receberá o ajuste.
        params: 
          - 'start': início do ajuste em segundos
          - 'end': fim do ajuste em segundos
          - parâmetros específicos do ajuste (ex: level, intensity)
        """
        self.strip_name = strip_name
        self.params = params

    def apply(self, seq, fps):
        """
        seq: VSE sequences_all
        fps: frames por segundo
        """
        raise NotImplementedError("Cada ajuste deve implementar apply()")
