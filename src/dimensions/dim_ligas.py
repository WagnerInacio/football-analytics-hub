import pandas as pd
from typing import List, Dict, Any


def build(leagues_raw: List[Dict[str, Any]]) -> pd.DataFrame:
    if not leagues_raw:
        return pd.DataFrame()

    rows = []
    for item in leagues_raw:
        l = item.get("league", {})
        c = item.get("country", {})
        rows.append({
            "liga_id":           l.get("id"),
            "nome":              l.get("name"),
            "tipo":              l.get("type"),
            "logo_url":          l.get("logo"),
            "pais_nome":         c.get("name"),
            "pais_codigo":       c.get("code"),
            "pais_bandeira_url": c.get("flag"),
        })

    return pd.DataFrame(rows).drop_duplicates("liga_id").reset_index(drop=True)
