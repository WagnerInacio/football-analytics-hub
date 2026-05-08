"""
Módulo dedicado à extração, transformação e salvamento da classificação.
Endpoint: GET /standings  (league=71, season=2024)
Saída:    data/processed/standings.csv  (pronto para Qlik Sense)
          data/facts/fato_classificacao.csv
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

from src.api_client import APIClient
from config import LEAGUE_ID, SEASON


# ── Fetch ─────────────────────────────────────────────────────────────────────

def fetch_standings(client: APIClient, logger) -> List[Dict[str, Any]]:
    """
    Busca a classificação via /standings.
    Usa o APIClient existente (já possui retry, timeout e tratamento HTTP).
    Retorna [] em caso de falha para não interromper o pipeline.
    """
    logger.info("[standings] Coletando classificação...")

    try:
        data = client.get("standings", {"league": LEAGUE_ID, "season": SEASON})

        if not data:
            logger.warning("[standings] Sem resposta da API.")
            return []

        response = data.get("response", [])
        if not response:
            logger.warning("[standings] Campo 'response' vazio.")
            return []

        return response

    except Exception as exc:
        logger.error(f"[standings] Erro inesperado na coleta: {exc}", exc_info=True)
        return []


# ── Transform ─────────────────────────────────────────────────────────────────

def transform_standings(raw: List[Dict[str, Any]], logger) -> pd.DataFrame:
    """
    Normaliza o JSON de standings em DataFrame estruturado para Qlik Sense.

    Campos gerados
    ──────────────
    Identificação : liga_id, temporada_id
    Classificação : posicao, pontos, saldo_gols, aproveitamento_pct,
                    forma, grupo, status, descricao
    Time          : team_id, team_nome, team_logo
    Geral         : jogos, vitorias, empates, derrotas, gols_pro, gols_contra
    Mandante      : jogos_casa, vitorias_casa, empates_casa, derrotas_casa,
                    gols_pro_casa, gols_contra_casa, aproveitamento_casa_pct
    Visitante     : jogos_fora, vitorias_fora, empates_fora, derrotas_fora,
                    gols_pro_fora, gols_contra_fora, aproveitamento_fora_pct
    """
    if not raw:
        logger.warning("[standings] Dados brutos vazios — transformação ignorada.")
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
                # Identificação
                "liga_id":                 liga_id,
                "temporada_id":            temporada_id,
                # Classificação
                "posicao":                 entry.get("rank"),
                "pontos":                  pontos,
                "saldo_gols":              entry.get("goalsDiff"),
                "aproveitamento_pct":      aprov(pontos, jogos),
                "forma":                   entry.get("form"),
                "grupo":                   entry.get("group"),
                "status":                  entry.get("status"),
                "descricao":               entry.get("description"),
                # Time
                "team_id":                 team.get("id"),
                "team_nome":               team.get("name"),
                "team_logo":               team.get("logo"),
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

        df = pd.DataFrame(rows)
        logger.info(f"[standings] {len(df)} times encontrados na classificação.")
        return df

    except Exception as exc:
        logger.error(f"[standings] Erro na transformação: {exc}", exc_info=True)
        return pd.DataFrame()


# ── Save ──────────────────────────────────────────────────────────────────────

def save_standings_csv(df: pd.DataFrame, path: Path, logger) -> bool:
    """Salva DataFrame em CSV UTF-8. Retorna True em caso de sucesso."""
    if df.empty:
        logger.warning(f"[standings] DataFrame vazio — {path.name} não salvo.")
        return False

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False, encoding="utf-8")
        logger.info(f"[standings] {path.name} salvo com sucesso em: {path.parent}")
        return True

    except Exception as exc:
        logger.error(f"[standings] Erro ao salvar {path.name}: {exc}")
        return False


# ── Pipeline helper ───────────────────────────────────────────────────────────

def run_standings_pipeline(
    client: APIClient,
    logger,
    processed_dir: Path,
    facts_dir: Path,
) -> pd.DataFrame:
    """
    Executa fetch → transform → save (processed + facts).
    Retorna o DataFrame para uso no star schema.
    Em caso de falha retorna DataFrame vazio (pipeline continua).
    """
    raw = fetch_standings(client, logger)
    df  = transform_standings(raw, logger)

    save_standings_csv(df, processed_dir / "standings.csv",          logger)
    save_standings_csv(df, facts_dir     / "fato_classificacao.csv", logger)

    return df
