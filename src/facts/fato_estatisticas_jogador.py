import pandas as pd
from typing import Dict, List, Any


def build(players_by_fixture: Dict[int, List[Dict[str, Any]]]) -> pd.DataFrame:
    """
    Constrói fato_estatisticas_jogador a partir de /fixtures/players.
    players_by_fixture: {fixture_id: resposta_do_endpoint}
    """
    if not players_by_fixture:
        return pd.DataFrame()

    rows = []
    row_id = 1
    for fixture_id, teams_data in players_by_fixture.items():
        for team_entry in teams_data:
            team = team_entry.get("team", {})
            for entry in team_entry.get("players", []):
                player = entry.get("player", {})
                for stats in entry.get("statistics", []):
                    games    = stats.get("games", {})
                    shots    = stats.get("shots", {})
                    goals    = stats.get("goals", {})
                    passes   = stats.get("passes", {})
                    tackles  = stats.get("tackles", {})
                    duels    = stats.get("duels", {})
                    dribbles = stats.get("dribbles", {})
                    fouls    = stats.get("fouls", {})
                    cards    = stats.get("cards", {})
                    pen      = stats.get("penalty", {})

                    rows.append({
                        "stat_id":            row_id,
                        "partida_id":         fixture_id,       # FK → fato_partidas
                        "team_id":            team.get("id"),   # FK → dim_times
                        "jogador_id":         player.get("id"), # FK → dim_jogadores
                        "numero":             games.get("number"),
                        "posicao":            games.get("position"),
                        "titular":            not games.get("substitute", True),
                        "minutos":            games.get("minutes"),
                        "rating":             games.get("rating"),
                        "capitao":            games.get("captain", False),
                        "chutes_total":       shots.get("total"),
                        "chutes_no_gol":      shots.get("on"),
                        "gols":               goals.get("total"),
                        "gols_sofridos":      goals.get("conceded"),
                        "assistencias":       goals.get("assists"),
                        "defesas":            goals.get("saves"),
                        "passes_total":       passes.get("total"),
                        "passes_chave":       passes.get("key"),
                        "precisao_passes":    passes.get("accuracy"),
                        "desarmes_total":     tackles.get("total"),
                        "bloqueios":          tackles.get("blocks"),
                        "interceptacoes":     tackles.get("interceptions"),
                        "duelos_total":       duels.get("total"),
                        "duelos_ganhos":      duels.get("won"),
                        "dribles_tentados":   dribbles.get("attempts"),
                        "dribles_sucesso":    dribbles.get("success"),
                        "faltas_sofridas":    fouls.get("drawn"),
                        "faltas_cometidas":   fouls.get("committed"),
                        "cartao_amarelo":     cards.get("yellow"),
                        "cartao_vermelho":    cards.get("red"),
                        "penalti_convertido": pen.get("scored"),
                        "penalti_perdido":    pen.get("missed"),
                    })
                    row_id += 1

    return pd.DataFrame(rows)
