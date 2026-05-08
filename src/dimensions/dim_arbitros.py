import pandas as pd
from typing import List, Dict, Any


def build(fixtures_raw: List[Dict[str, Any]]) -> pd.DataFrame:
    """Extrai árbitros únicos a partir das partidas."""
    if not fixtures_raw:
        return pd.DataFrame()

    nomes = set()
    for item in fixtures_raw:
        ref = item.get("fixture", {}).get("referee")
        if ref:
            nomes.add(ref.strip())

    if not nomes:
        return pd.DataFrame()

    rows = [
        {"arbitro_id": i + 1, "nome": nome}
        for i, nome in enumerate(sorted(nomes))
    ]
    return pd.DataFrame(rows)
