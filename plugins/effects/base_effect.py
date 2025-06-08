# plugins/effects/base_effect.py

class BaseEffect:
    """
    Interface que todo plugin de efeito deve seguir.
    Cada efeito deve implementar:
      - name: string única correspondente ao identificador no JSON.
      - apply(self, seq, audio_seq, fps): inserir lógica do efeito na sequência.
    """
    name = "base_effect"

    def __init__(self, start_time: float, end_time: float, params: dict):
        self.start_time = start_time
        self.end_time = end_time
        self.params = params

    def apply(self, seq, audio_seq, fps):
        raise NotImplementedError("Cada efeito deve implementar apply()")
