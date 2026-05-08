import pandas as pd
from typing import List, Dict, Any


def build(squads_raw: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Constrói dim_jogadores a partir das respostas do endpoint /players/squads.
    squads_raw é a lista acumulada de todos os times (cada item tem 'team' e 'players').
    """
    if not squads_raw:
        return pd.DataFrame()

    rows = []
    for entry in squads_raw:
        team = entry.get("team", {})
        for p in entry.get("players", []):
            rows.append({
                "jogador_id": p.get("id"),
                "nome":       p.get("name"),
                "idade":      p.get("age"),
                "numero":     p.get("number"),
                "posicao":    p.get("position"),
                "foto_url":   p.get("photo"),
                "team_id":    team.get("id"),   # FK → dim_times (time atual)
            })

    if not rows:
        return pd.DataFrame()

    return (
        pd.DataFrame(rows)
        .drop_duplicates("jogador_id")
        .reset_index(drop=True)
    )
