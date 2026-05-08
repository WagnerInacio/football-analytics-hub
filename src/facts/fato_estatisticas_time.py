import pandas as pd
from typing import List, Dict, Any


def build(team_stats_list: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Constrói fato_estatisticas_time a partir das respostas de /teams/statistics.
    Cada item é a resposta completa para um time na liga/temporada.
    """
    if not team_stats_list:
        return pd.DataFrame()

    rows = []
    for ts in team_stats_list:
        team   = ts.get("team", {})
        league = ts.get("league", {})
        fx     = ts.get("fixtures", {})
        goals  = ts.get("goals", {})
        pen    = ts.get("penalty", {})
        clean  = ts.get("clean_sheet", {})
        failed = ts.get("failed_to_score", {})
        biggest = ts.get("biggest", {})

        rows.append({
            "team_id":              team.get("id"),       # FK → dim_times
            "liga_id":              league.get("id"),     # FK → dim_ligas
            "temporada_id":         league.get("season"), # FK → dim_temporadas
            "forma":                ts.get("form"),
            # Partidas
            "jogos_casa":           fx.get("played", {}).get("home"),
            "jogos_fora":           fx.get("played", {}).get("away"),
            "jogos_total":          fx.get("played", {}).get("total"),
            "vitorias_casa":        fx.get("wins", {}).get("home"),
            "vitorias_fora":        fx.get("wins", {}).get("away"),
            "vitorias_total":       fx.get("wins", {}).get("total"),
            "empates_casa":         fx.get("draws", {}).get("home"),
            "empates_fora":         fx.get("draws", {}).get("away"),
            "empates_total":        fx.get("draws", {}).get("total"),
            "derrotas_casa":        fx.get("loses", {}).get("home"),
            "derrotas_fora":        fx.get("loses", {}).get("away"),
            "derrotas_total":       fx.get("loses", {}).get("total"),
            # Gols marcados
            "gols_pro_casa":        goals.get("for", {}).get("total", {}).get("home"),
            "gols_pro_fora":        goals.get("for", {}).get("total", {}).get("away"),
            "gols_pro_total":       goals.get("for", {}).get("total", {}).get("total"),
            "media_gols_pro":       goals.get("for", {}).get("average", {}).get("total"),
            # Gols sofridos
            "gols_contra_casa":     goals.get("against", {}).get("total", {}).get("home"),
            "gols_contra_fora":     goals.get("against", {}).get("total", {}).get("away"),
            "gols_contra_total":    goals.get("against", {}).get("total", {}).get("total"),
            "media_gols_contra":    goals.get("against", {}).get("average", {}).get("total"),
            # Pênaltis
            "penaltis_marcados":    pen.get("scored", {}).get("total"),
            "penaltis_perdidos":    pen.get("missed", {}).get("total"),
            "penaltis_total":       pen.get("total"),
            # Extras
            "clean_sheets":         clean.get("total"),
            "sem_marcar":           failed.get("total"),
            "sequencia_vitorias":   biggest.get("streak", {}).get("wins"),
            "sequencia_empates":    biggest.get("streak", {}).get("draws"),
            "sequencia_derrotas":   biggest.get("streak", {}).get("loses"),
        })

    return pd.DataFrame(rows)
