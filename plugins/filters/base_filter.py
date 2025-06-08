# plugins/filters/base_filter.py

class BaseFilter:
    """
    Interface para filtros de cor/look geral (vinheta, granulado, color balance etc.).
    Cada filtro é aplicado a uma strip ou a toda a cena.
    """
    name = "base_filter"

    def __init__(self, strip_name: str, params: dict):
        """
        strip_name: nome da strip alvo (ou 'all' para toda a cena).
        params: parâmetros específicos (cor, intensidade, etc.).
        """
        self.strip_name = strip_name
        self.params = params

    def apply(self, seq, fps):
        raise NotImplementedError("Cada filtro deve implementar apply()")
