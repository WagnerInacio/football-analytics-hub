import pandas as pd
from typing import Dict, List, Any

_DETAIL_MAP = {
    "Yellow Card":      "amarelo",
    "Red Card":         "vermelho",
    "Yellow Red Card":  "segundo_amarelo",
}


def build(events_by_fixture: Dict[int, List[Dict[str, Any]]]) -> pd.DataFrame:
    """
    Extrai cartões a partir dos eventos por partida.
    events_by_fixture: {fixture_id: [evento, ...]}
    """
    if not events_by_fixture:
        return pd.DataFrame()

    rows = []
    cartao_id = 1
    for fixture_id, events in events_by_fixture.items():
        for event in events:
            if event.get("type") != "Card":
                continue

            detail = event.get("detail", "")
            tipo = _DETAIL_MAP.get(detail, detail.lower())

            time_info = event.get("time", {})
            p = event.get("player", {})
            t = event.get("team", {})

            rows.append({
                "cartao_id":    cartao_id,
                "partida_id":   fixture_id,     # FK → fato_partidas
                "time_id":      t.get("id"),    # FK → dim_times
                "player_id":    p.get("id"),
                "player_nome":  p.get("name"),
                "minuto":       time_info.get("elapsed"),
                "minuto_extra": time_info.get("extra"),
                "tipo_cartao":  tipo,           # amarelo, vermelho, segundo_amarelo
            })
            cartao_id += 1

    return pd.DataFrame(rows)
