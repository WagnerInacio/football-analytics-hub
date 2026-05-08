import pandas as pd
from typing import List, Dict, Any, Optional


def _flat(data: List[Dict[str, Any]]) -> pd.DataFrame:
    if not data:
        return pd.DataFrame()
    df = pd.json_normalize(data)
    df.columns = [c.replace(".", "_").lower() for c in df.columns]
    return df


class Transformer:
    def __init__(self, logger):
        self.logger = logger

    # ── Liga & Temporada ──────────────────────────────────────────────────────

    def normalize_leagues(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        return _flat(data)

    # ── Times & Estádios ─────────────────────────────────────────────────────

    def normalize_teams(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        return _flat(data)

    def normalize_venues(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        return _flat(data)

    def normalize_team_statistics(
        self,
        team_stats_list: List[Dict[str, Any]],
    ) -> pd.DataFrame:
        """
        Recebe lista de respostas de /teams/statistics (uma por time).
        Achata os campos principais em colunas.
        """
        if not team_stats_list:
            return pd.DataFrame()

        rows = []
        for ts in team_stats_list:
            team = ts.get("team", {})
            league = ts.get("league", {})
            fx = ts.get("fixtures", {})
            goals = ts.get("goals", {})
            penalty = ts.get("penalty", {})
            clean = ts.get("clean_sheet", {})
            failed = ts.get("failed_to_score", {})
            biggest = ts.get("biggest", {})

            rows.append({
                "team_id":            team.get("id"),
                "team_nome":          team.get("name"),
                "liga_id":            league.get("id"),
                "temporada":          league.get("season"),
                "forma":              ts.get("form"),
                # Partidas jogadas
                "jogos_casa":         fx.get("played", {}).get("home"),
                "jogos_fora":         fx.get("played", {}).get("away"),
                "jogos_total":        fx.get("played", {}).get("total"),
                # Vitórias / Empates / Derrotas
                "vitorias_casa":      fx.get("wins", {}).get("home"),
                "vitorias_fora":      fx.get("wins", {}).get("away"),
                "vitorias_total":     fx.get("wins", {}).get("total"),
                "empates_casa":       fx.get("draws", {}).get("home"),
                "empates_fora":       fx.get("draws", {}).get("away"),
                "empates_total":      fx.get("draws", {}).get("total"),
                "derrotas_casa":      fx.get("loses", {}).get("home"),
                "derrotas_fora":      fx.get("loses", {}).get("away"),
                "derrotas_total":     fx.get("loses", {}).get("total"),
                # Gols marcados
                "gols_pro_casa":      goals.get("for", {}).get("total", {}).get("home"),
                "gols_pro_fora":      goals.get("for", {}).get("total", {}).get("away"),
                "gols_pro_total":     goals.get("for", {}).get("total", {}).get("total"),
                "media_gols_pro":     goals.get("for", {}).get("average", {}).get("total"),
                # Gols sofridos
                "gols_contra_casa":   goals.get("against", {}).get("total", {}).get("home"),
                "gols_contra_fora":   goals.get("against", {}).get("total", {}).get("away"),
                "gols_contra_total":  goals.get("against", {}).get("total", {}).get("total"),
                "media_gols_contra":  goals.get("against", {}).get("average", {}).get("total"),
                # Pênaltis
                "penaltis_marcados":  penalty.get("scored", {}).get("total"),
                "penaltis_perdidos":  penalty.get("missed", {}).get("total"),
                "penaltis_total":     penalty.get("total"),
                # Extras
                "clean_sheets_total": clean.get("total"),
                "sem_marcar_total":   failed.get("total"),
                "maior_sequencia_vit":biggest.get("streak", {}).get("wins"),
                "maior_sequencia_emp":biggest.get("streak", {}).get("draws"),
                "maior_sequencia_der":biggest.get("streak", {}).get("loses"),
            })

        return pd.DataFrame(rows)

    # ── Partidas (Fixtures) ───────────────────────────────────────────────────

    def normalize_fixtures(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        df = _flat(data)
        if "fixture_date" in df.columns:
            df["fixture_date"] = pd.to_datetime(df["fixture_date"])
        # Garante coluna fixture_id mesmo que o json_normalize use nome diferente
        if "fixture_id" not in df.columns and "fixture_id" in df.columns:
            pass  # já existe
        return df

    def normalize_fixture_stats(
        self,
        data: List[Dict[str, Any]],
        fixture_id: int,
    ) -> pd.DataFrame:
        rows = []
        for team_stats in data:
            team_id = team_stats["team"]["id"]
            team_name = team_stats["team"]["name"]
            for stat in team_stats.get("statistics", []):
                rows.append({
                    "fixture_id": fixture_id,
                    "team_id":    team_id,
                    "team_name":  team_name,
                    "tipo":       stat["type"],
                    "valor":      stat["value"],
                })
        return pd.DataFrame(rows)

    def normalize_fixture_players(
        self,
        players_by_fixture: Dict[int, List[Dict[str, Any]]],
    ) -> pd.DataFrame:
        """Achata estatísticas individuais dos jogadores por partida."""
        rows = []
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
                            "fixture_id":         fixture_id,
                            "team_id":            team.get("id"),
                            "player_id":          player.get("id"),
                            "player_nome":        player.get("name"),
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

        return pd.DataFrame(rows)

    def normalize_lineups(
        self,
        lineups_by_fixture: Dict[int, List[Dict[str, Any]]],
    ) -> pd.DataFrame:
        """Achata escalações (titulares + banco) de cada partida."""
        rows = []
        for fixture_id, teams_lineups in lineups_by_fixture.items():
            for team_entry in teams_lineups:
                team = team_entry.get("team", {})
                formation = team_entry.get("formation")
                coach = team_entry.get("coach", {})

                for role, players in [
                    ("titular", team_entry.get("startXI", [])),
                    ("banco",   team_entry.get("substitutes", [])),
                ]:
                    for p_entry in players:
                        p = p_entry.get("player", {})
                        rows.append({
                            "fixture_id":   fixture_id,
                            "team_id":      team.get("id"),
                            "formacao":     formation,
                            "tecnico_id":   coach.get("id"),
                            "tecnico_nome": coach.get("name"),
                            "player_id":    p.get("id"),
                            "player_nome":  p.get("name"),
                            "numero":       p.get("number"),
                            "posicao":      p.get("pos"),
                            "grade":        p.get("grid"),
                            "papel":        role,
                        })

        return pd.DataFrame(rows)

    # ── Classificação ─────────────────────────────────────────────────────────

    def normalize_standings(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        if not data:
            return pd.DataFrame()
        standings_list = data[0]["league"]["standings"][0]
        return _flat(standings_list)

    # ── Jogadores ─────────────────────────────────────────────────────────────

    def normalize_top_scorers(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        return _flat(data)

    def normalize_top_assists(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        return _flat(data)

    def normalize_top_yellow_cards(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        return _flat(data)

    def normalize_top_red_cards(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        return _flat(data)

    def normalize_squads(self, squads_raw: List[Dict[str, Any]]) -> pd.DataFrame:
        """Achata elencos de times em uma tabela de jogadores."""
        rows = []
        for entry in squads_raw:
            team = entry.get("team", {})
            for p in entry.get("players", []):
                rows.append({
                    "player_id":  p.get("id"),
                    "nome":       p.get("name"),
                    "idade":      p.get("age"),
                    "numero":     p.get("number"),
                    "posicao":    p.get("position"),
                    "foto_url":   p.get("photo"),
                    "team_id":    team.get("id"),
                    "team_nome":  team.get("name"),
                })
        return pd.DataFrame(rows).drop_duplicates("player_id").reset_index(drop=True) if rows else pd.DataFrame()

    def normalize_coaches(self, coaches_raw: List[Dict[str, Any]]) -> pd.DataFrame:
        rows = []
        for coach in coaches_raw:
            team = coach.get("team", {})
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
                "team_id":       team.get("id"),
                "team_nome":     team.get("name"),
            })
        return pd.DataFrame(rows).drop_duplicates("tecnico_id").reset_index(drop=True) if rows else pd.DataFrame()

    # ── Lesões ────────────────────────────────────────────────────────────────

    def normalize_injuries(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        rows = []
        for item in data:
            player  = item.get("player", {})
            team    = item.get("team", {})
            fixture = item.get("fixture", {})
            league  = item.get("league", {})
            rows.append({
                "player_id":    player.get("id"),
                "player_nome":  player.get("name"),
                "tipo_lesao":   player.get("type"),
                "motivo":       player.get("reason"),
                "team_id":      team.get("id"),
                "team_nome":    team.get("name"),
                "fixture_id":   fixture.get("id"),
                "data":         fixture.get("date"),
                "liga_id":      league.get("id"),
                "temporada":    league.get("season"),
            })
        return pd.DataFrame(rows)

    # ── Transferências ────────────────────────────────────────────────────────

    def normalize_transfers(self, transfers_raw: List[Dict[str, Any]]) -> pd.DataFrame:
        rows = []
        for item in transfers_raw:
            player = item.get("player", {})
            for t in item.get("transfers", []):
                rows.append({
                    "player_id":      player.get("id"),
                    "player_nome":    player.get("name"),
                    "data":           t.get("date"),
                    "tipo":           t.get("type"),
                    "team_origem_id": t.get("teams", {}).get("out", {}).get("id"),
                    "team_origem":    t.get("teams", {}).get("out", {}).get("name"),
                    "team_destino_id":t.get("teams", {}).get("in", {}).get("id"),
                    "team_destino":   t.get("teams", {}).get("in", {}).get("name"),
                })
        return pd.DataFrame(rows)
