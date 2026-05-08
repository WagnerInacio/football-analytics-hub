from pathlib import Path
from typing import Dict, List, Any

import pandas as pd

from src.dimensions import (
    dim_times,
    dim_estadios,
    dim_ligas,
    dim_temporadas,
    dim_arbitros,
    dim_datas,
    dim_jogadores,
    dim_tecnicos,
    dim_rodadas,
)
from src.facts import (
    fato_partidas,
    fato_gols,
    fato_resultados,
    fato_cartoes,
    fato_substituicoes,
    fato_estatisticas_time,
    fato_estatisticas_jogador,
    fato_classificacao,
)
from src.load import Loader


class StarSchemaBuilder:
    def __init__(self, logger, dimensions_dir: Path, facts_dir: Path):
        self.logger = logger
        self.dimensions_dir = dimensions_dir
        self.facts_dir = facts_dir
        self.loader = Loader(logger)

    def build(
        self,
        leagues_raw: List[Dict[str, Any]],
        teams_raw: List[Dict[str, Any]],
        fixtures_raw: List[Dict[str, Any]],
        standings_raw: List[Dict[str, Any]] | None = None,
        squads_raw: List[Dict[str, Any]] | None = None,
        coaches_raw: List[Dict[str, Any]] | None = None,
        team_stats_list: List[Dict[str, Any]] | None = None,
        events_by_fixture: Dict[int, List[Dict[str, Any]]] | None = None,
        players_by_fixture: Dict[int, List[Dict[str, Any]]] | None = None,
        rounds_raw: List[str] | None = None,
    ) -> None:

        self.logger.info("=" * 50)
        self.logger.info("CONSTRUINDO STAR SCHEMA")
        self.logger.info("=" * 50)

        # ── Dimensões ────────────────────────────────────────────────────────
        self.logger.info("Processando dimensões...")

        dim_times_df = dim_times.build(teams_raw)
        self.loader.save_to_csv(dim_times_df, self.dimensions_dir / "dim_times.csv")

        dim_estadios_df = dim_estadios.build(teams_raw)
        self.loader.save_to_csv(dim_estadios_df, self.dimensions_dir / "dim_estadios.csv")

        dim_ligas_df = dim_ligas.build(leagues_raw)
        self.loader.save_to_csv(dim_ligas_df, self.dimensions_dir / "dim_ligas.csv")

        dim_temporadas_df = dim_temporadas.build(leagues_raw)
        self.loader.save_to_csv(dim_temporadas_df, self.dimensions_dir / "dim_temporadas.csv")

        dim_arbitros_df = dim_arbitros.build(fixtures_raw)
        self.loader.save_to_csv(dim_arbitros_df, self.dimensions_dir / "dim_arbitros.csv")

        dim_datas_df = dim_datas.build(fixtures_raw)
        self.loader.save_to_csv(dim_datas_df, self.dimensions_dir / "dim_datas.csv")

        if squads_raw:
            dim_jogadores_df = dim_jogadores.build(squads_raw)
            self.loader.save_to_csv(dim_jogadores_df, self.dimensions_dir / "dim_jogadores.csv")

        if coaches_raw:
            dim_tecnicos_df = dim_tecnicos.build(coaches_raw)
            self.loader.save_to_csv(dim_tecnicos_df, self.dimensions_dir / "dim_tecnicos.csv")

        dim_rodadas_df = pd.DataFrame()
        if rounds_raw:
            dim_rodadas_df = dim_rodadas.build(rounds_raw)
            self.loader.save_to_csv(dim_rodadas_df, self.dimensions_dir / "dim_rodadas.csv")

        # ── Fatos ────────────────────────────────────────────────────────────
        self.logger.info("Processando fatos...")

        fato_partidas_df = fato_partidas.build(fixtures_raw, dim_arbitros_df, dim_rodadas_df)
        self.loader.save_to_csv(fato_partidas_df, self.facts_dir / "fato_partidas.csv")

        fato_resultados_df = fato_resultados.build(fixtures_raw)
        self.loader.save_to_csv(fato_resultados_df, self.facts_dir / "fato_resultados.csv")

        if team_stats_list:
            fato_est_time_df = fato_estatisticas_time.build(team_stats_list)
            self.loader.save_to_csv(fato_est_time_df, self.facts_dir / "fato_estatisticas_time.csv")

        if events_by_fixture:
            fato_gols_df = fato_gols.build(events_by_fixture)
            self.loader.save_to_csv(fato_gols_df, self.facts_dir / "fato_gols.csv")

            fato_cartoes_df = fato_cartoes.build(events_by_fixture)
            self.loader.save_to_csv(fato_cartoes_df, self.facts_dir / "fato_cartoes.csv")

            fato_subs_df = fato_substituicoes.build(events_by_fixture)
            self.loader.save_to_csv(fato_subs_df, self.facts_dir / "fato_substituicoes.csv")
        else:
            self.logger.warning(
                "Sem eventos de partida — fato_gols, fato_cartoes e "
                "fato_substituicoes não foram gerados."
            )

        if players_by_fixture:
            fato_est_jog_df = fato_estatisticas_jogador.build(players_by_fixture)
            self.loader.save_to_csv(fato_est_jog_df, self.facts_dir / "fato_estatisticas_jogador.csv")

        if standings_raw:
            fato_class_df = fato_classificacao.build(standings_raw)
            self.loader.save_to_csv(fato_class_df, self.facts_dir / "fato_classificacao.csv")

        self.logger.info("Star Schema construído com sucesso.")
        self.logger.info(
            f"  Dimensões salvas em: {self.dimensions_dir.name}/  "
            f"| Fatos salvos em: {self.facts_dir.name}/"
        )
