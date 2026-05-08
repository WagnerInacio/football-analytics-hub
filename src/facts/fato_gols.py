import pandas as pd
from typing import Dict, List, Any

_DETAIL_TO_TIPO = {
    "Normal Goal":     "normal",
    "Penalty":         "penalti",
    "Own Goal":        "gol_contra",
    "Missed Penalty":  None,   # não é gol — ignorar
}


def build(events_by_fixture: Dict[int, List[Dict[str, Any]]]) -> pd.DataFrame:
    """
    Constrói fato_gols a partir dos eventos por partida.

    Parâmetro:
        events_by_fixture: {fixture_id: [evento, ...]}
    """
    if not events_by_fixture:
        return pd.DataFrame()

    rows = []
    gol_id = 1
    for fixture_id, events in events_by_fixture.items():
        for event in events:
            if event.get("type") != "Goal":
                continue

            detail = event.get("detail", "")
            tipo = _DETAIL_TO_TIPO.get(detail, "normal")
            if tipo is None:
                continue   # pênalti perdido — não registra como gol

            time_info = event.get("time", {})
            p = event.get("player", {})
            a = event.get("assist", {})
            t = event.get("team", {})

            rows.append({
                "gol_id":             gol_id,
                "partida_id":         fixture_id,   # FK → fato_partidas
                "time_id":            t.get("id"),  # FK → dim_times
                "player_id":          p.get("id"),
                "player_nome":        p.get("name"),
                "assist_player_id":   a.get("id"),
                "assist_player_nome": a.get("name"),
                "minuto":             time_info.get("elapsed"),
                "minuto_extra":       time_info.get("extra"),
                "tipo_gol":           tipo,
                "detalhe":            detail,
            })
            gol_id += 1

    return pd.DataFrame(rows)
