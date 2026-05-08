import pandas as pd
from typing import List, Dict, Any


def build(raw: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Constrói fato_classificacao a partir do raw de /standings.
    Mantém FKs alinhadas com as dimensões do star schema:
      team_id      → dim_times
      liga_id      → dim_ligas
      temporada_id → dim_temporadas
    """
    if not raw:
        return pd.DataFrame()

    try:
        league_data    = raw[0].get("league", {})
        standings_list = league_data.get("standings", [[]])[0]

        liga_id      = league_data.get("id")
        temporada_id = league_data.get("season")

        def aprov(pts: int, jogos: int) -> float:
            return round(pts / (jogos * 3) * 100, 1) if jogos > 0 else 0.0

        rows = []
        for entry in standings_list:
            team   = entry.get("team",  {})
            all_s  = entry.get("all",   {})
            home_s = entry.get("home",  {})
            away_s = entry.get("away",  {})

            jogos      = all_s.get("played")  or 0
            jogos_casa = home_s.get("played") or 0
            jogos_fora = away_s.get("played") or 0
            pontos     = entry.get("points")  or 0
            vit_casa   = home_s.get("win")    or 0
            vit_fora   = away_s.get("win")    or 0
            emp_casa   = home_s.get("draw")   or 0
            emp_fora   = away_s.get("draw")   or 0

            rows.append({
                # FKs para o star schema
                "liga_id":                 liga_id,
                "temporada_id":            temporada_id,
                "team_id":                 team.get("id"),
                # Classificação
                "posicao":                 entry.get("rank"),
                "pontos":                  pontos,
                "saldo_gols":              entry.get("goalsDiff"),
                "aproveitamento_pct":      aprov(pontos, jogos),
                "forma":                   entry.get("form"),
                "grupo":                   entry.get("group"),
                "status":                  entry.get("status"),
                "descricao":               entry.get("description"),
                # Geral
                "jogos":                   jogos,
                "vitorias":                all_s.get("win"),
                "empates":                 all_s.get("draw"),
                "derrotas":                all_s.get("lose"),
                "gols_pro":                all_s.get("goals", {}).get("for"),
                "gols_contra":             all_s.get("goals", {}).get("against"),
                # Mandante
                "jogos_casa":              jogos_casa,
                "vitorias_casa":           vit_casa,
                "empates_casa":            emp_casa,
                "derrotas_casa":           home_s.get("lose"),
                "gols_pro_casa":           home_s.get("goals", {}).get("for"),
                "gols_contra_casa":        home_s.get("goals", {}).get("against"),
                "aproveitamento_casa_pct": aprov(vit_casa * 3 + emp_casa, jogos_casa),
                # Visitante
                "jogos_fora":              jogos_fora,
                "vitorias_fora":           vit_fora,
                "empates_fora":            emp_fora,
                "derrotas_fora":           away_s.get("lose"),
                "gols_pro_fora":           away_s.get("goals", {}).get("for"),
                "gols_contra_fora":        away_s.get("goals", {}).get("against"),
                "aproveitamento_fora_pct": aprov(vit_fora * 3 + emp_fora, jogos_fora),
                # Auditoria
                "ultima_atualizacao":      entry.get("update"),
            })

        return pd.DataFrame(rows)

    except Exception:
        return pd.DataFrame()
