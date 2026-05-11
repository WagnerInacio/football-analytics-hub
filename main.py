import sys
import pandas as pd
from datetime import datetime
from config import (
    LOGS_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR,
    DIMENSIONS_DIR, FACTS_DIR, MAX_DAILY_REQUESTS,
    QLIK_DIMENSIONS_DIR, QLIK_FACTS_DIR,
)
from src.logger import setup_logger
from src.api_client import APIClient
from src.extract import Extractor
from src.transform import Transformer
from src.load import Loader
from src.star_schema import StarSchemaBuilder
from src.extract_standings import run_standings_pipeline


def main():
    # ── Setup ─────────────────────────────────────────────────────────────────
    log_file = LOGS_DIR / f"pipeline_{datetime.now().strftime('%Y%m%d')}.log"
    logger = setup_logger("FootballPipeline", log_file)

    logger.info("=" * 50)
    logger.info("INICIANDO PIPELINE DE DADOS: API-FOOTBALL")
    logger.info("=" * 50)

    client      = APIClient(logger)
    extractor   = Extractor(client, logger)
    transformer = Transformer(logger)
    loader      = Loader(logger)
    star_builder = StarSchemaBuilder(
        logger, DIMENSIONS_DIR, FACTS_DIR,
        extra_dimensions_dirs=[QLIK_DIMENSIONS_DIR],
        extra_facts_dirs=[QLIK_FACTS_DIR],
    )

    try:
        # ── 1. Dados Base (Liga, Times, Estádios) ─────────────────────────────

        logger.info("Processando Ligas...")
        leagues_raw = extractor.get_leagues()
        loader.save_to_csv(transformer.normalize_leagues(leagues_raw), RAW_DATA_DIR / "leagues.csv")

        logger.info("Processando Times...")
        teams_raw = extractor.get_teams()
        loader.save_to_csv(transformer.normalize_teams(teams_raw), RAW_DATA_DIR / "teams.csv")

        logger.info("Processando Estádios...")
        venues_raw = extractor.get_venues()
        loader.save_to_csv(transformer.normalize_venues(venues_raw), RAW_DATA_DIR / "venues.csv")

        logger.info("Processando Rodadas...")
        rounds_raw = extractor.get_rounds()
        loader.save_to_csv(
            pd.DataFrame({"rodada": rounds_raw}), RAW_DATA_DIR / "rounds.csv"
        )

        # ── 2. Partidas & Classificação ───────────────────────────────────────

        logger.info("Processando Partidas (Fixtures)...")
        fixtures_raw = extractor.get_fixtures()
        fixtures_df  = transformer.normalize_fixtures(fixtures_raw)
        loader.save_to_csv(fixtures_df, RAW_DATA_DIR / "fixtures.csv")

        # ── 2b. Classificação (pipeline dedicado) ────────────────────────────
        run_standings_pipeline(
            client=client,
            logger=logger,
            processed_dir=PROCESSED_DATA_DIR,
            facts_dir=FACTS_DIR,
            qlik_facts_dir=QLIK_FACTS_DIR,
        )
        # Mantém raw simples para compatibilidade e auditoria
        standings_raw = extractor.get_standings()
        loader.save_to_csv(transformer.normalize_standings(standings_raw), RAW_DATA_DIR / "standings_raw.csv")

        # ── 3. Rankings de Jogadores ──────────────────────────────────────────

        logger.info("Processando Artilheiros...")
        scorers_raw = extractor.get_top_scorers()
        loader.save_to_csv(transformer.normalize_top_scorers(scorers_raw), PROCESSED_DATA_DIR / "top_scorers.csv")

        logger.info("Processando Assistências...")
        assists_raw = extractor.get_top_assists()
        loader.save_to_csv(transformer.normalize_top_assists(assists_raw), PROCESSED_DATA_DIR / "top_assists.csv")

        logger.info("Processando Cartões Amarelos...")
        yellow_raw = extractor.get_top_yellow_cards()
        loader.save_to_csv(transformer.normalize_top_yellow_cards(yellow_raw), PROCESSED_DATA_DIR / "top_yellow_cards.csv")

        logger.info("Processando Cartões Vermelhos...")
        red_raw = extractor.get_top_red_cards()
        loader.save_to_csv(transformer.normalize_top_red_cards(red_raw), PROCESSED_DATA_DIR / "top_red_cards.csv")

        # ── 4. Lesões ─────────────────────────────────────────────────────────

        logger.info("Processando Lesões...")
        injuries_raw = extractor.get_injuries()
        loader.save_to_csv(transformer.normalize_injuries(injuries_raw), PROCESSED_DATA_DIR / "injuries.csv")

        # ── 5. Dados por Time (Elenco, Técnico, Estatísticas) ─────────────────

        logger.info("Processando dados por time (elenco, técnico, estatísticas)...")
        bulk_teams = extractor.get_teams_bulk(
            teams_raw,
            fetch_squads=True,
            fetch_coaches=True,
            fetch_stats=True,
        )

        squads_raw     = bulk_teams["squads"]
        coaches_raw    = bulk_teams["coaches"]
        team_stats_list = bulk_teams["team_stats"]

        loader.save_to_csv(transformer.normalize_squads(squads_raw), RAW_DATA_DIR / "squads.csv")
        loader.save_to_csv(transformer.normalize_coaches(coaches_raw), RAW_DATA_DIR / "coaches.csv")
        loader.save_to_csv(
            transformer.normalize_team_statistics(team_stats_list),
            PROCESSED_DATA_DIR / "team_statistics.csv",
        )

        # ── 6. Dados por Partida (Eventos, Escalações, Stats, Jogadores) ──────

        logger.info("Processando dados por partida (eventos, escalações, estatísticas)...")
        bulk_fixtures = extractor.get_fixtures_bulk(
            fixtures_raw,
            fetch_stats=True,
            fetch_events=True,
            fetch_lineups=True,
            fetch_players=True,
        )

        stats_by_fixture   = bulk_fixtures["stats_by_fixture"]
        events_by_fixture  = bulk_fixtures["events_by_fixture"]
        lineups_by_fixture = bulk_fixtures["lineups_by_fixture"]
        players_by_fixture = bulk_fixtures["players_by_fixture"]

        # Estatísticas de partida (flat)
        if stats_by_fixture:
            all_stats = [
                transformer.normalize_fixture_stats(stats, fid)
                for fid, stats in stats_by_fixture.items()
            ]
            loader.save_to_csv(
                pd.concat(all_stats, ignore_index=True),
                PROCESSED_DATA_DIR / "fixture_statistics.csv",
            )

        # Escalações
        if lineups_by_fixture:
            loader.save_to_csv(
                transformer.normalize_lineups(lineups_by_fixture),
                PROCESSED_DATA_DIR / "lineups.csv",
            )

        # Estatísticas de jogadores por partida
        if players_by_fixture:
            loader.save_to_csv(
                transformer.normalize_fixture_players(players_by_fixture),
                PROCESSED_DATA_DIR / "fixture_players.csv",
            )

        # ── 7. Star Schema ────────────────────────────────────────────────────

        star_builder.build(
            leagues_raw=leagues_raw,
            teams_raw=teams_raw,
            fixtures_raw=fixtures_raw,
            standings_raw=standings_raw or None,
            squads_raw=squads_raw or None,
            coaches_raw=coaches_raw or None,
            team_stats_list=team_stats_list or None,
            events_by_fixture=events_by_fixture or None,
            players_by_fixture=players_by_fixture or None,
            rounds_raw=rounds_raw or None,
        )

        # ── Sumário ───────────────────────────────────────────────────────────
        logger.info("=" * 50)
        logger.info("PIPELINE CONCLUÍDO COM SUCESSO")
        logger.info(f"Requests realizados: {client.request_count}/{MAX_DAILY_REQUESTS}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Erro crítico no pipeline: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
