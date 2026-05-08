-- ============================================================
-- STAR SCHEMA — API Football v3
-- ============================================================

-- ── DIMENSÕES ────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dim_times (
    time_id     INT           PRIMARY KEY,
    nome        VARCHAR(255)  NOT NULL,
    codigo      VARCHAR(10),
    pais        VARCHAR(100),
    fundado     INT,
    is_nacional BOOLEAN       DEFAULT FALSE,
    logo_url    TEXT
);

CREATE TABLE IF NOT EXISTS dim_estadios (
    estadio_id  INT           PRIMARY KEY,
    nome        VARCHAR(255),
    cidade      VARCHAR(100),
    capacidade  INT,
    superficie  VARCHAR(50),
    endereco    TEXT,
    imagem_url  TEXT
);

CREATE TABLE IF NOT EXISTS dim_ligas (
    liga_id           INT          PRIMARY KEY,
    nome              VARCHAR(255) NOT NULL,
    tipo              VARCHAR(50),
    logo_url          TEXT,
    pais_nome         VARCHAR(100),
    pais_codigo       VARCHAR(10),
    pais_bandeira_url TEXT
);

CREATE TABLE IF NOT EXISTS dim_temporadas (
    temporada_id  INT      PRIMARY KEY,   -- ano (ex.: 2024)
    ano           INT      NOT NULL,
    inicio        DATE,
    fim           DATE,
    em_andamento  BOOLEAN  DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS dim_arbitros (
    arbitro_id  SERIAL       PRIMARY KEY,
    nome        VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_datas (
    data_id         INT         PRIMARY KEY,  -- YYYYMMDD
    data            DATE        NOT NULL,
    dia             SMALLINT,
    mes             SMALLINT,
    ano             SMALLINT,
    trimestre       SMALLINT,
    dia_semana      SMALLINT,                 -- 1=Segunda … 7=Domingo
    nome_dia_semana VARCHAR(20),
    nome_mes        VARCHAR(20),
    is_fim_semana   BOOLEAN     DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS dim_jogadores (
    jogador_id  INT          PRIMARY KEY,
    nome        VARCHAR(255) NOT NULL,
    idade       SMALLINT,
    numero      SMALLINT,
    posicao     VARCHAR(50),
    foto_url    TEXT,
    team_id     INT          REFERENCES dim_times(time_id)
);

CREATE TABLE IF NOT EXISTS dim_tecnicos (
    tecnico_id    INT          PRIMARY KEY,
    nome          VARCHAR(255) NOT NULL,
    primeiro_nome VARCHAR(100),
    sobrenome     VARCHAR(100),
    idade         SMALLINT,
    nacionalidade VARCHAR(100),
    data_nasc     DATE,
    local_nasc    VARCHAR(100),
    pais_nasc     VARCHAR(100),
    altura        VARCHAR(20),
    peso          VARCHAR(20),
    foto_url      TEXT,
    team_id       INT          REFERENCES dim_times(time_id)
);

CREATE TABLE IF NOT EXISTS dim_rodadas (
    rodada_id      INT          PRIMARY KEY,
    rodada         VARCHAR(100) NOT NULL,  -- ex.: "Regular Season - 1"
    fase           VARCHAR(100),           -- ex.: "Regular Season"
    numero_rodada  SMALLINT
);

-- ── FATOS ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS fato_partidas (
    partida_id        INT         PRIMARY KEY,
    data_id           INT         REFERENCES dim_datas(data_id),
    liga_id           INT         REFERENCES dim_ligas(liga_id),
    temporada_id      INT         REFERENCES dim_temporadas(temporada_id),
    rodada_id         INT         REFERENCES dim_rodadas(rodada_id),
    time_casa_id      INT         REFERENCES dim_times(time_id),
    time_visitante_id INT         REFERENCES dim_times(time_id),
    estadio_id        INT         REFERENCES dim_estadios(estadio_id),
    arbitro_id        INT         REFERENCES dim_arbitros(arbitro_id),
    status            VARCHAR(50),
    status_codigo     VARCHAR(10),
    minuto_elapsed    SMALLINT
);

CREATE TABLE IF NOT EXISTS fato_resultados (
    resultado_id       SERIAL   PRIMARY KEY,
    partida_id         INT      REFERENCES fato_partidas(partida_id),
    time_casa_id       INT      REFERENCES dim_times(time_id),
    time_visitante_id  INT      REFERENCES dim_times(time_id),
    gols_casa_ht       SMALLINT,
    gols_visitante_ht  SMALLINT,
    gols_casa_ft       SMALLINT,
    gols_visitante_ft  SMALLINT,
    gols_casa_et       SMALLINT,
    gols_visitante_et  SMALLINT,
    gols_casa_ps       SMALLINT,
    gols_visitante_ps  SMALLINT,
    resultado          CHAR(1),              -- H=casa, D=empate, A=visitante
    winner_id          INT      REFERENCES dim_times(time_id)
);

CREATE TABLE IF NOT EXISTS fato_gols (
    gol_id              SERIAL        PRIMARY KEY,
    partida_id          INT           REFERENCES fato_partidas(partida_id),
    time_id             INT           REFERENCES dim_times(time_id),
    player_id           INT,
    player_nome         VARCHAR(255),
    assist_player_id    INT,
    assist_player_nome  VARCHAR(255),
    minuto              SMALLINT,
    minuto_extra        SMALLINT,
    tipo_gol            VARCHAR(20),   -- normal, penalti, gol_contra
    detalhe             VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS fato_cartoes (
    cartao_id    SERIAL       PRIMARY KEY,
    partida_id   INT          REFERENCES fato_partidas(partida_id),
    time_id      INT          REFERENCES dim_times(time_id),
    player_id    INT,
    player_nome  VARCHAR(255),
    minuto       SMALLINT,
    minuto_extra SMALLINT,
    tipo_cartao  VARCHAR(20)  -- amarelo, vermelho, segundo_amarelo
);

CREATE TABLE IF NOT EXISTS fato_substituicoes (
    substituicao_id      SERIAL       PRIMARY KEY,
    partida_id           INT          REFERENCES fato_partidas(partida_id),
    time_id              INT          REFERENCES dim_times(time_id),
    jogador_saiu_id      INT,
    jogador_saiu_nome    VARCHAR(255),
    jogador_entrou_id    INT,
    jogador_entrou_nome  VARCHAR(255),
    minuto               SMALLINT,
    minuto_extra         SMALLINT
);

CREATE TABLE IF NOT EXISTS fato_estatisticas_time (
    team_id              INT   REFERENCES dim_times(time_id),
    liga_id              INT   REFERENCES dim_ligas(liga_id),
    temporada_id         INT   REFERENCES dim_temporadas(temporada_id),
    forma                VARCHAR(50),
    jogos_total          SMALLINT,
    jogos_casa           SMALLINT,
    jogos_fora           SMALLINT,
    vitorias_total       SMALLINT,
    vitorias_casa        SMALLINT,
    vitorias_fora        SMALLINT,
    empates_total        SMALLINT,
    empates_casa         SMALLINT,
    empates_fora         SMALLINT,
    derrotas_total       SMALLINT,
    derrotas_casa        SMALLINT,
    derrotas_fora        SMALLINT,
    gols_pro_total       SMALLINT,
    gols_pro_casa        SMALLINT,
    gols_pro_fora        SMALLINT,
    media_gols_pro       NUMERIC(5,2),
    gols_contra_total    SMALLINT,
    gols_contra_casa     SMALLINT,
    gols_contra_fora     SMALLINT,
    media_gols_contra    NUMERIC(5,2),
    penaltis_marcados    SMALLINT,
    penaltis_perdidos    SMALLINT,
    penaltis_total       SMALLINT,
    clean_sheets         SMALLINT,
    sem_marcar           SMALLINT,
    sequencia_vitorias   SMALLINT,
    sequencia_empates    SMALLINT,
    sequencia_derrotas   SMALLINT,
    PRIMARY KEY (team_id, liga_id, temporada_id)
);

CREATE TABLE IF NOT EXISTS fato_estatisticas_jogador (
    stat_id              SERIAL        PRIMARY KEY,
    partida_id           INT           REFERENCES fato_partidas(partida_id),
    team_id              INT           REFERENCES dim_times(time_id),
    jogador_id           INT           REFERENCES dim_jogadores(jogador_id),
    numero               SMALLINT,
    posicao              VARCHAR(5),
    titular              BOOLEAN,
    minutos              SMALLINT,
    rating               NUMERIC(4,1),
    capitao              BOOLEAN,
    chutes_total         SMALLINT,
    chutes_no_gol        SMALLINT,
    gols                 SMALLINT,
    gols_sofridos        SMALLINT,
    assistencias         SMALLINT,
    defesas              SMALLINT,
    passes_total         SMALLINT,
    passes_chave         SMALLINT,
    precisao_passes      SMALLINT,
    desarmes_total       SMALLINT,
    bloqueios            SMALLINT,
    interceptacoes       SMALLINT,
    duelos_total         SMALLINT,
    duelos_ganhos        SMALLINT,
    dribles_tentados     SMALLINT,
    dribles_sucesso      SMALLINT,
    faltas_sofridas      SMALLINT,
    faltas_cometidas     SMALLINT,
    cartao_amarelo       SMALLINT,
    cartao_vermelho      SMALLINT,
    penalti_convertido   SMALLINT,
    penalti_perdido      SMALLINT
);

CREATE TABLE IF NOT EXISTS fato_classificacao (
    liga_id                 INT           REFERENCES dim_ligas(liga_id),
    temporada_id            INT           REFERENCES dim_temporadas(temporada_id),
    team_id                 INT           REFERENCES dim_times(time_id),
    -- Classificação
    posicao                 SMALLINT      NOT NULL,
    pontos                  SMALLINT,
    saldo_gols              SMALLINT,
    aproveitamento_pct      NUMERIC(5,1),
    forma                   VARCHAR(10),
    grupo                   VARCHAR(100),
    status                  VARCHAR(50),
    descricao               TEXT,
    -- Geral
    jogos                   SMALLINT,
    vitorias                SMALLINT,
    empates                 SMALLINT,
    derrotas                SMALLINT,
    gols_pro                SMALLINT,
    gols_contra             SMALLINT,
    -- Mandante
    jogos_casa              SMALLINT,
    vitorias_casa           SMALLINT,
    empates_casa            SMALLINT,
    derrotas_casa           SMALLINT,
    gols_pro_casa           SMALLINT,
    gols_contra_casa        SMALLINT,
    aproveitamento_casa_pct NUMERIC(5,1),
    -- Visitante
    jogos_fora              SMALLINT,
    vitorias_fora           SMALLINT,
    empates_fora            SMALLINT,
    derrotas_fora           SMALLINT,
    gols_pro_fora           SMALLINT,
    gols_contra_fora        SMALLINT,
    aproveitamento_fora_pct NUMERIC(5,1),
    -- Auditoria
    ultima_atualizacao      TIMESTAMP,
    PRIMARY KEY (liga_id, temporada_id, team_id)
);
