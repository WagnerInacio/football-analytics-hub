import pandas as pd
from typing import List, Dict, Any


def build(coaches_raw: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Constrói dim_tecnicos a partir das respostas do endpoint /coachs.
    coaches_raw é a lista acumulada de todas as respostas por time.
    """
    if not coaches_raw:
        return pd.DataFrame()

    rows = []
    for coach in coaches_raw:
        team  = coach.get("team", {})
        birth = coach.get("birth", {})
        rows.append({
            "tecnico_id":    coach.get("id"),
            "nome":          coach.get("name"),
            "primeiro_nome": coach.get("firstname"),
            "sobrenome":     coach.get("lastname"),
            "idade":         coach.get("age"),
            "nacionalidade": coach.get("nationality"),
            "data_nasc":     birth.get("date"),
            "local_nasc":    birth.get("place"),
            "pais_nasc":     birth.get("country"),
            "altura":        coach.get("height"),
            "peso":          coach.get("weight"),
            "foto_url":      coach.get("photo"),
            "team_id":       team.get("id"),   # FK → dim_times (time atual)
        })

    if not rows:
        return pd.DataFrame()

    return (
        pd.DataFrame(rows)
        .drop_duplicates("tecnico_id")
        .reset_index(drop=True)
    )
