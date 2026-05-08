import pandas as pd
from typing import List, Dict, Any


def build(teams_raw: List[Dict[str, Any]]) -> pd.DataFrame:
    if not teams_raw:
        return pd.DataFrame()

    rows = []
    for item in teams_raw:
        t = item.get("team", {})
        rows.append({
            "time_id":    t.get("id"),
            "nome":       t.get("name"),
            "codigo":     t.get("code"),
            "pais":       t.get("country"),
            "fundado":    t.get("founded"),
            "is_nacional": t.get("national", False),
            "logo_url":   t.get("logo"),
        })

    return pd.DataFrame(rows).drop_duplicates("time_id").reset_index(drop=True)
