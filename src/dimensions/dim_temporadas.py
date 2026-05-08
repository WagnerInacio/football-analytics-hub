import pandas as pd
from typing import List, Dict, Any


def build(leagues_raw: List[Dict[str, Any]]) -> pd.DataFrame:
    """Extrai temporadas da resposta da API de ligas (campo 'seasons')."""
    if not leagues_raw:
        return pd.DataFrame()

    seen = set()
    rows = []
    for item in leagues_raw:
        for season in item.get("seasons", []):
            year = season.get("year")
            if year is None or year in seen:
                continue
            seen.add(year)
            rows.append({
                "temporada_id":  year,
                "ano":           year,
                "inicio":        season.get("start"),
                "fim":           season.get("end"),
                "em_andamento":  season.get("current", False),
            })

    if not rows:
        return pd.DataFrame()

    return (
        pd.DataFrame(rows)
        .sort_values("ano")
        .reset_index(drop=True)
    )
