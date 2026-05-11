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
    def __init__(
        self,
        logger,
        dimensions_dir: Path,
        facts_dir: Path,
        extra_dimensions_dirs: list[Path] | None = None,
        extra_facts_dirs: list[Path] | None = None,
    ):
        self.logger = logger
        self.dim_dirs  = [dimensions_dir]  + (extra_dimensions_dirs or [])
        self.fact_dirs = [facts_dir] + (extra_facts_dirs or [])
        self.loader = Loader(logger)

    def _save_dim(self, df: pd.DataFrame, filename: str) -> None:
        for d in self.dim_dirs:
            self.loader.save_to_csv(df, d / filename)

    def _save_fact(self, df: pd.DataFrame, filename: str) -> None:
        for d in self.fact_dirs:
            self.loader.save_to_csv(df, d / filename)

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

        # Prioritárias — sempre salvas
        dim_times_df = dim_times.build(teams_raw)
        self._save_dim(dim_times_df, "dim_times.csv")

        dim_ligas_df = dim_ligas.build(leagues_raw)
        self._save_dim(dim_ligas_df, "dim_ligas.csv")

        dim_temporadas_df = dim_temporadas.build(leagues_raw)
        self._save_dim(dim_temporadas_df, "dim_temporadas.csv")

        dim_rodadas_df = dim_rodadas.build(rounds_raw or [])
        self._save_dim(dim_rodadas_df, "dim_rodadas.csv")

        # Complementares
        dim_estadios_df = dim_estadios.build(teams_raw)
        self._save_dim(dim_estadios_df, "dim_estadios.csv")

        dim_arbitros_df = dim_arbitros.build(fixtures_raw)
        self._save_dim(dim_arbitros_df, "dim_arbitros.csv")

        dim_datas_df = dim_datas.build(fixtures_raw)
        self._save_dim(dim_datas_df, "dim_datas.csv")

        if squads_raw:
            dim_jogadores_df = dim_jogadores.build(squads_raw)
            self._save_dim(dim_jogadores_df, "dim_jogadores.csv")

        if coaches_raw:
            dim_tecnicos_df = dim_tecnicos.build(coaches_raw)
            self._save_dim(dim_tecnicos_df, "dim_tecnicos.csv")

        # ── Fatos ────────────────────────────────────────────────────────────
        self.logger.info("Processando fatos...")

        # Prioritários — sempre salvos
        fato_partidas_df = fato_partidas.build(fixtures_raw, dim_arbitros_df, dim_rodadas_df)
        self._save_fact(fato_partidas_df, "fato_partidas.csv")

        fato_class_df = fato_classificacao.build(standings_raw or [])
        self._save_fact(fato_class_df, "fato_classificacao.csv")

        # Complementares
        fato_resultados_df = fato_resultados.build(fixtures_raw)
        self._save_fact(fato_resultados_df, "fato_resultados.csv")

        if team_stats_list:
            fato_est_time_df = fato_estatisticas_time.build(team_stats_list)
            self._save_fact(fato_est_time_df, "fato_estatisticas_time.csv")

        if events_by_fixture:
            fato_gols_df = fato_gols.build(events_by_fixture)
            self._save_fact(fato_gols_df, "fato_gols.csv")

            fato_cartoes_df = fato_cartoes.build(events_by_fixture)
            self._save_fact(fato_cartoes_df, "fato_cartoes.csv")

            fato_subs_df = fato_substituicoes.build(events_by_fixture)
            self._save_fact(fato_subs_df, "fato_substituicoes.csv")
        else:
            self.logger.warning(
                "Sem eventos de partida — fato_gols, fato_cartoes e "
                "fato_substituicoes não foram gerados."
            )

        if players_by_fixture:
            fato_est_jog_df = fato_estatisticas_jogador.build(players_by_fixture)
            self._save_fact(fato_est_jog_df, "fato_estatisticas_jogador.csv")

        self.logger.info("Star Schema construído com sucesso.")
        self.logger.info(
            f"  Dimensões salvas em: {self.dim_dirs[0].name}/  "
            f"| Fatos salvos em: {self.fact_dirs[0].name}/"
        )
