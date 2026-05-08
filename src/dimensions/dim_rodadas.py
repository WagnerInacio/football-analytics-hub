import pandas as pd
from typing import List


def build(rounds_raw: List[str]) -> pd.DataFrame:
    """Constrói a dimensão de rodadas a partir da lista de strings retornada pela API."""
    if not rounds_raw:
        return pd.DataFrame()

    rows = []
    for idx, rodada in enumerate(rounds_raw, start=1):
        partes = rodada.rsplit(" - ", 1)
        fase = partes[0] if len(partes) == 2 else rodada
        try:
            numero = int(partes[1]) if len(partes) == 2 else idx
        except ValueError:
            numero = idx

        rows.append({
            "rodada_id":     idx,
            "rodada":        rodada,
            "fase":          fase,
            "numero_rodada": numero,
        })

    return pd.DataFrame(rows)
