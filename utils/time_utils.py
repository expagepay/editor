from typing import Final


def sec2frame(sec: float, fps: int) -> int:
    """Converte segundos (float) em número inteiro de frames."""
    return int(round(sec * fps))
