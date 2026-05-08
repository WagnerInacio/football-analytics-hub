import pandas as pd
from typing import List, Dict, Any


def build(fixtures_raw: List[Dict[str, Any]]) -> pd.DataFrame:
    if not fixtures_raw:
        return pd.DataFrame()

    rows = []
    for i, item in enumerate(fixtures_raw):
        f = item.get("fixture", {})
        t = item.get("teams", {})
        s = item.get("score", {})

        home = t.get("home", {})
        away = t.get("away", {})

        gols_casa_ft = s.get("fulltime", {}).get("home")
        gols_vis_ft  = s.get("fulltime", {}).get("away")

        resultado = None
        winner_id = None
        if gols_casa_ft is not None and gols_vis_ft is not None:
            if gols_casa_ft > gols_vis_ft:
                resultado = "H"
                winner_id = home.get("id")
            elif gols_casa_ft < gols_vis_ft:
                resultado = "A"
                winner_id = away.get("id")
            else:
                resultado = "D"

        rows.append({
            "resultado_id":        i + 1,
            "partida_id":          f.get("id"),        # FK → fato_partidas
            "time_casa_id":        home.get("id"),     # FK → dim_times
            "time_visitante_id":   away.get("id"),     # FK → dim_times
            "gols_casa_ht":        s.get("halftime",  {}).get("home"),
            "gols_visitante_ht":   s.get("halftime",  {}).get("away"),
            "gols_casa_ft":        gols_casa_ft,
            "gols_visitante_ft":   gols_vis_ft,
            "gols_casa_et":        s.get("extratime", {}).get("home"),
            "gols_visitante_et":   s.get("extratime", {}).get("away"),
            "gols_casa_ps":        s.get("penalty",   {}).get("home"),
            "gols_visitante_ps":   s.get("penalty",   {}).get("away"),
            "resultado":           resultado,  # H=casa, D=empate, A=visitante
            "winner_id":           winner_id,  # FK → dim_times (nullable)
        })

    return pd.DataFrame(rows)
