import pandas as pd
from typing import List, Dict, Any


def build(teams_raw: List[Dict[str, Any]]) -> pd.DataFrame:
    if not teams_raw:
        return pd.DataFrame()

    rows = []
    for item in teams_raw:
        v = item.get("venue", {})
        if not v.get("id"):
            continue
        rows.append({
            "estadio_id":  v.get("id"),
            "nome":        v.get("name"),
            "cidade":      v.get("city"),
            "capacidade":  v.get("capacity"),
            "superficie":  v.get("surface"),
            "endereco":    v.get("address"),
            "imagem_url":  v.get("image"),
        })

    return pd.DataFrame(rows).drop_duplicates("estadio_id").reset_index(drop=True)
