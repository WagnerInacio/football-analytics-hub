import pandas as pd
from typing import List, Dict, Any


def build(
    fixtures_raw: List[Dict[str, Any]],
    arbitros_df: pd.DataFrame,
    rodadas_df: pd.DataFrame,
) -> pd.DataFrame:
    if not fixtures_raw:
        return pd.DataFrame()

    ref_lookup: Dict[str, int] = {}
    if not arbitros_df.empty:
        ref_lookup = dict(zip(arbitros_df["nome"], arbitros_df["arbitro_id"]))

    rodada_lookup: Dict[str, int] = {}
    if not rodadas_df.empty:
        rodada_lookup = dict(zip(rodadas_df["rodada"], rodadas_df["rodada_id"]))

    rows = []
    for item in fixtures_raw:
        f = item.get("fixture", {})
        l = item.get("league", {})
        t = item.get("teams", {})

        date_str = f.get("date")
        data_id = int(pd.Timestamp(date_str).strftime("%Y%m%d")) if date_str else None

        ref_nome = f.get("referee", "").strip() if f.get("referee") else None
        rodada_str = l.get("round")

        rows.append({
            "partida_id":        f.get("id"),
            "data_id":           data_id,                                           # FK → dim_datas
            "liga_id":           l.get("id"),                                       # FK → dim_ligas
            "temporada_id":      l.get("season"),                                   # FK → dim_temporadas
            "rodada_id":         rodada_lookup.get(rodada_str) if rodada_str else None,  # FK → dim_rodadas
            "time_casa_id":      t.get("home", {}).get("id"),                       # FK → dim_times
            "time_visitante_id": t.get("away", {}).get("id"),                       # FK → dim_times
            "estadio_id":        f.get("venue", {}).get("id"),                      # FK → dim_estadios
            "arbitro_id":        ref_lookup.get(ref_nome) if ref_nome else None,    # FK → dim_arbitros
            "status":            f.get("status", {}).get("long"),
            "status_codigo":     f.get("status", {}).get("short"),
            "minuto_elapsed":    f.get("status", {}).get("elapsed"),
        })

    return pd.DataFrame(rows)
