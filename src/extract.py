from typing import List, Dict, Any, Optional
from src.api_client import APIClient
from config import LEAGUE_ID, SEASON, FIXTURE_LIMIT, TEAM_STATS_LIMIT, FIXTURE_PLAYER_LIMIT


class Extractor:
    def __init__(self, client: APIClient, logger):
        self.client = client
        self.logger = logger

    # ── Liga & Temporada ──────────────────────────────────────────────────────

    def get_leagues(self) -> List[Dict[str, Any]]:
        data = self.client.get("leagues", {"id": LEAGUE_ID})
        return data.get("response", []) if data else []

    def get_rounds(self) -> List[str]:
        data = self.client.get("fixtures/rounds", {"league": LEAGUE_ID, "season": SEASON})
        return data.get("response", []) if data else []

    # ── Times & Estádios ─────────────────────────────────────────────────────

    def get_teams(self) -> List[Dict[str, Any]]:
        data = self.client.get("teams", {"league": LEAGUE_ID, "season": SEASON})
        return data.get("response", []) if data else []

    def get_venues(self) -> List[Dict[str, Any]]:
        data = self.client.get("venues", {"league": LEAGUE_ID, "season": SEASON})
        return data.get("response", []) if data else []

    def get_team_statistics(self, team_id: int) -> Optional[Dict[str, Any]]:
        data = self.client.get("teams/statistics", {
            "league": LEAGUE_ID, "season": SEASON, "team": team_id,
        })
        resp = data.get("response", {}) if data else {}
        return resp if resp else None

    # ── Partidas (Fixtures) ───────────────────────────────────────────────────

    def get_fixtures(self) -> List[Dict[str, Any]]:
        data = self.client.get("fixtures", {
            "league": LEAGUE_ID,
            "season": SEASON,
        })
        response = data.get("response", []) if data else []
        return response[:FIXTURE_LIMIT] if FIXTURE_LIMIT else response

    def get_fixtures_by_round(self, round_name: str) -> List[Dict[str, Any]]:
        data = self.client.get("fixtures", {
            "league": LEAGUE_ID,
            "season": SEASON,
            "round": round_name,
        })
        return data.get("response", []) if data else []

    def get_fixture_details(self, fixture_id: int) -> Dict[str, Any]:
        """Busca estatísticas, eventos e escalações de uma partida específica."""
        details: Dict[str, Any] = {}

        stats = self.client.get("fixtures/statistics", {"fixture": fixture_id})
        details["statistics"] = stats.get("response", []) if stats else []

        events = self.client.get("fixtures/events", {"fixture": fixture_id})
        details["events"] = events.get("response", []) if events else []

        lineups = self.client.get("fixtures/lineups", {"fixture": fixture_id})
        details["lineups"] = lineups.get("response", []) if lineups else []

        return details

    def get_fixture_players(self, fixture_id: int) -> List[Dict[str, Any]]:
        """Busca estatísticas individuais dos jogadores em uma partida."""
        data = self.client.get("fixtures/players", {"fixture": fixture_id})
        return data.get("response", []) if data else []

    def get_head_to_head(self, team1_id: int, team2_id: int, last: int = 10) -> List[Dict[str, Any]]:
        data = self.client.get("fixtures/headtohead", {
            "h2h": f"{team1_id}-{team2_id}",
            "last": last,
        })
        return data.get("response", []) if data else []

    # ── Classificação ─────────────────────────────────────────────────────────

    def get_standings(self) -> List[Dict[str, Any]]:
        data = self.client.get("standings", {"league": LEAGUE_ID, "season": SEASON})
        return data.get("response", []) if data else []

    # ── Jogadores ─────────────────────────────────────────────────────────────

    def get_squad(self, team_id: int) -> List[Dict[str, Any]]:
        data = self.client.get("players/squads", {"team": team_id})
        return data.get("response", []) if data else []

    def get_top_scorers(self) -> List[Dict[str, Any]]:
        data = self.client.get("players/topscorers", {"league": LEAGUE_ID, "season": SEASON})
        return data.get("response", []) if data else []

    def get_top_assists(self) -> List[Dict[str, Any]]:
        data = self.client.get("players/topassists", {"league": LEAGUE_ID, "season": SEASON})
        return data.get("response", []) if data else []

    def get_top_yellow_cards(self) -> List[Dict[str, Any]]:
        data = self.client.get("players/topyellowcards", {"league": LEAGUE_ID, "season": SEASON})
        return data.get("response", []) if data else []

    def get_top_red_cards(self) -> List[Dict[str, Any]]:
        data = self.client.get("players/topredcards", {"league": LEAGUE_ID, "season": SEASON})
        return data.get("response", []) if data else []

    # ── Técnicos ─────────────────────────────────────────────────────────────

    def get_coach(self, team_id: int) -> List[Dict[str, Any]]:
        data = self.client.get("coachs", {"team": team_id})
        return data.get("response", []) if data else []

    # ── Lesões & Transferências ───────────────────────────────────────────────

    def get_injuries(self) -> List[Dict[str, Any]]:
        data = self.client.get("injuries", {"league": LEAGUE_ID, "season": SEASON})
        return data.get("response", []) if data else []

    def get_transfers(self, team_id: int) -> List[Dict[str, Any]]:
        data = self.client.get("transfers", {"team": team_id})
        return data.get("response", []) if data else []

    # ── Previsões ─────────────────────────────────────────────────────────────

    def get_predictions(self, fixture_id: int) -> Optional[Dict[str, Any]]:
        data = self.client.get("predictions", {"fixture": fixture_id})
        resp = data.get("response", []) if data else []
        return resp[0] if resp else None

    # ── Países & Fusos ────────────────────────────────────────────────────────

    def get_countries(self) -> List[Dict[str, Any]]:
        data = self.client.get("countries", {})
        return data.get("response", []) if data else []

    # ── Helpers ───────────────────────────────────────────────────────────────

    def get_teams_bulk(
        self,
        teams_raw: List[Dict[str, Any]],
        fetch_squads: bool = True,
        fetch_coaches: bool = True,
        fetch_stats: bool = True,
    ) -> Dict[str, Any]:
        """
        Busca dados por time (elenco, técnico, estatísticas) respeitando TEAM_STATS_LIMIT.
        Retorna dicionários indexados por team_id.
        """
        result: Dict[str, Any] = {
            "squads": [],
            "coaches": [],
            "team_stats": [],
        }

        teams = teams_raw[:TEAM_STATS_LIMIT]
        for item in teams:
            team_id = item.get("team", {}).get("id")
            if not team_id:
                continue

            if fetch_squads:
                squad = self.get_squad(team_id)
                result["squads"].extend(squad)

            if fetch_coaches:
                coach = self.get_coach(team_id)
                result["coaches"].extend(coach)

            if fetch_stats:
                stats = self.get_team_statistics(team_id)
                if stats:
                    result["team_stats"].append(stats)

        return result

    def get_fixtures_bulk(
        self,
        fixtures_raw: List[Dict[str, Any]],
        fetch_stats: bool = True,
        fetch_events: bool = True,
        fetch_lineups: bool = True,
        fetch_players: bool = True,
    ) -> Dict[str, Any]:
        """
        Busca dados detalhados por partida respeitando FIXTURE_LIMIT e FIXTURE_PLAYER_LIMIT.
        """
        result: Dict[str, Any] = {
            "stats_by_fixture": {},
            "events_by_fixture": {},
            "lineups_by_fixture": {},
            "players_by_fixture": {},
        }

        detail_limit = min(len(fixtures_raw), FIXTURE_LIMIT)
        player_limit = min(len(fixtures_raw), FIXTURE_PLAYER_LIMIT)

        for idx, item in enumerate(fixtures_raw[:detail_limit]):
            fixture_id = item.get("fixture", {}).get("id")
            if not fixture_id:
                continue

            details = self.get_fixture_details(fixture_id)

            if fetch_stats and details["statistics"]:
                result["stats_by_fixture"][fixture_id] = details["statistics"]

            if fetch_events and details["events"]:
                result["events_by_fixture"][fixture_id] = details["events"]

            if fetch_lineups and details["lineups"]:
                result["lineups_by_fixture"][fixture_id] = details["lineups"]

            if fetch_players and idx < player_limit:
                players = self.get_fixture_players(fixture_id)
                if players:
                    result["players_by_fixture"][fixture_id] = players

        return result
