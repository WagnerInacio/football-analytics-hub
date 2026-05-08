import pandas as pd
from typing import Dict, List, Any


def build(events_by_fixture: Dict[int, List[Dict[str, Any]]]) -> pd.DataFrame:
    """
    Extrai substituições a partir dos eventos por partida.
    events_by_fixture: {fixture_id: [evento, ...]}
    """
    if not events_by_fixture:
        return pd.DataFrame()

    rows = []
    sub_id = 1
    for fixture_id, events in events_by_fixture.items():
        for event in events:
            if event.get("type") != "subst":
                continue

            time_info = event.get("time", {})
            saiu  = event.get("player", {})   # jogador que saiu
            entrou = event.get("assist", {})  # jogador que entrou
            t = event.get("team", {})

            rows.append({
                "substituicao_id":     sub_id,
                "partida_id":          fixture_id,     # FK → fato_partidas
                "time_id":             t.get("id"),    # FK → dim_times
                "jogador_saiu_id":     saiu.get("id"),
                "jogador_saiu_nome":   saiu.get("name"),
                "jogador_entrou_id":   entrou.get("id"),
                "jogador_entrou_nome": entrou.get("name"),
                "minuto":              time_info.get("elapsed"),
                "minuto_extra":        time_info.get("extra"),
            })
            sub_id += 1

    return pd.DataFrame(rows)
