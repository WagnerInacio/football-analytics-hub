# Pipeline de Dados da API-Football/API-Sports

## 1. Visão Geral do Projeto

Este projeto implementa um pipeline de dados em Python para extrair, transformar e carregar (ETL) informações de futebol da [API-Football/API-Sports](https://www.api-football.com/). O objetivo é construir uma solução robusta, modular e escalável, focada inicialmente na coleta de dados do Brasileirão Série A da temporada atual, otimizada para o plano gratuito da API (100 requisições/dia). Os dados são salvos em arquivos CSV organizados, seguindo uma arquitetura de engenharia de dados Bronze/Silver.

## 2. Arquitetura do Pipeline

O pipeline segue uma arquitetura modular, dividida em componentes de Extração, Transformação e Carga, com módulos auxiliares para logging e validação. A estrutura de dados adota o conceito de camadas Bronze e Silver:

-   **Bronze**: Dados brutos, diretamente da API, salvos em CSVs na pasta `data/raw`.
-   **Silver**: Dados tratados e normalizados, prontos para análise, salvos em CSVs na pasta `data/processed`.

O projeto é preparado para futuras expansões, incluindo integração com bancos de dados como DuckDB, SQL Server, PostgreSQL e ferramentas como dbt e Airflow.

## 3. Como Instalar Dependências

Para configurar o ambiente e instalar as dependências necessárias, siga os passos abaixo:

1.  **Clone o repositório** (se aplicável, ou navegue até a pasta do projeto):
    ```bash
    cd football_pipeline
    ```

2.  **Crie e ative um ambiente virtual** (recomendado):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate  # Windows
    ```

3.  **Instale as dependências** usando o `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## 4. Como Configurar o `.env`

As credenciais da API e outras configurações sensíveis são gerenciadas através de variáveis de ambiente, carregadas pelo arquivo `.env`.

1.  **Crie uma cópia do arquivo `.env.example`** e renomeie-o para `.env` na raiz do projeto:
    ```bash
    cp .env.example .env
    ```

2.  **Edite o arquivo `.env`** e preencha com suas credenciais e configurações. O arquivo `.env.example` já contém os parâmetros padrão e um exemplo de chave:

    ```ini
    API_KEY=YOUR_API_KEY_HERE
    BASE_URL=https://v3.football.api-sports.io
    REQUEST_DELAY=2
    MAX_RETRIES=3
    TIMEOUT=30
    LEAGUE_ID=71
    SEASON=2024
    FIXTURE_LIMIT=20
    MAX_DAILY_REQUESTS=100
    ```

## 5. Onde Inserir a API Key

Para obter sua API Key e inseri-la no projeto:

1.  **Crie uma conta** na [API-Football/API-Sports](https://www.api-football.com/).
2.  **Copie a chave da sua conta** (geralmente encontrada no painel de controle ou seção de API).
3.  **Cole a chave no arquivo `.env`** que você criou no passo anterior, substituindo `YOUR_API_KEY_HERE` pelo valor real da sua chave.

    Exemplo:
    ```ini
    API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

## 6. Como Executar

Após configurar o ambiente e o arquivo `.env`, você pode executar o pipeline a partir da raiz do projeto:

```bash
python main.py
```

Ao executar, o pipeline irá:

-   Conectar-se à API-Football/API-Sports.
-   Buscar os dados configurados (ligas, times, partidas, etc.).
-   Tratar e normalizar os dados utilizando `pandas`.
-   Salvar os dados em arquivos CSV nas pastas `data/raw` e `data/processed`.
-   Gerar logs detalhados da execução na pasta `data/logs`.
-   Informar um resumo da execução no terminal, incluindo o número de requisições realizadas.

## 7. Estrutura das Pastas

```
/project-root
│
├── main.py             # Ponto de entrada principal do pipeline
├── config.py           # Configurações do projeto e variáveis de ambiente
├── requirements.txt    # Dependências do Python
├── README.md           # Este arquivo
├── .env.example        # Exemplo de arquivo de variáveis de ambiente
├── .gitignore          # Arquivos e pastas a serem ignorados pelo Git
│
├── /src                # Código fonte do pipeline
│   ├── api_client.py   # Cliente para interagir com a API-Football
│   ├── extract.py      # Lógica de extração de dados da API
│   ├── transform.py    # Lógica de transformação e normalização de dados
│   ├── load.py         # Lógica de carregamento de dados para CSV
│   ├── utils.py        # Funções utilitárias (e.g., delay)
│   ├── logger.py       # Configuração e gerenciamento de logs
│   └── validators.py   # Funções de validação de dados
│
├── /data               # Armazenamento dos dados
│   ├── raw             # Dados brutos (camada Bronze)
│   ├── processed       # Dados tratados e normalizados (camada Silver)
│   └── logs            # Logs de execução do pipeline
│
└── /sql                # Scripts SQL para futuras integrações de banco de dados
    └── create_tables.sql # Exemplo de script para criação de tabelas
```

## 8. Explicação das Tabelas CSV

Os dados são organizados em arquivos CSV, categorizados por sua camada de processamento:

### `data/raw` (Camada Bronze)

-   `leagues.csv`: Informações básicas sobre as ligas.
-   `teams.csv`: Detalhes sobre os times.
-   `fixtures.csv`: Informações sobre as partidas (jogos).
-   `standings.csv`: Classificação atual das ligas.

### `data/processed` (Camada Silver)

-   `fixture_statistics.csv`: Estatísticas detalhadas de cada partida (posse de bola, chutes, etc.).
-   `fixture_events.csv`: Eventos ocorridos durante as partidas (gols, cartões, substituições).
-   `lineups.csv`: Escalações dos times para cada partida.
-   `top_scorers.csv`: Lista dos artilheiros da liga.
-   `referees.csv`: Informações sobre os árbitros.
-   `stadiums.csv`: Informações sobre os estádios.

## 9. Estratégia de Economia de Requisições

Para otimizar o uso do plano gratuito da API (100 requisições/dia), o pipeline implementa as seguintes estratégias:

-   **Foco Inicial**: Prioriza a coleta de dados do Brasileirão Série A e da temporada atual.
-   **Requisições Seletivas**: Primeiro busca dados gerais (ligas, temporadas, times, partidas) e, em seguida, busca detalhes (estatísticas, eventos, escalações) apenas para um número limitado de jogos recentes (configurável via `FIXTURE_LIMIT`).
-   **Parâmetros Configuráveis**: Utiliza variáveis de ambiente (`LEAGUE_ID`, `SEASON`, `FIXTURE_LIMIT`, `MAX_DAILY_REQUESTS`) para controlar o escopo da coleta.
-   **Delay entre Requisições**: Um atraso configurável (`REQUEST_DELAY`) é aplicado entre as chamadas da API para evitar exceder os limites de taxa.
-   **Retry Automático**: Mecanismo de re-tentativa com *backoff* exponencial para lidar com falhas temporárias da rede ou da API.

## 10. Melhorias Futuras

O projeto foi desenhado com a expansibilidade em mente. Algumas melhorias futuras planejadas incluem:

-   **Suporte a Múltiplas Ligas e Temporadas**: Expandir a coleta para incluir dados de outras ligas e temporadas históricas.
-   **Integração com Banco de Dados**: Armazenar os dados em um banco de dados relacional (e.g., DuckDB, PostgreSQL, SQL Server) para facilitar consultas e análises.
-   **Ferramentas de Orquestração**: Utilizar ferramentas como Apache Airflow para orquestrar e agendar a execução do pipeline.
-   **Modelagem de Dados com dbt**: Implementar o dbt (data build tool) para transformar e modelar os dados na camada Gold, criando tabelas analíticas prontas para consumo.
-   **Monitoramento e Alertas**: Adicionar monitoramento para o status do pipeline e alertas em caso de falhas.
-   **Cache/Checkpoint Local**: Implementar um sistema de cache ou checkpoint para evitar requisições repetidas para dados que não mudam frequentemente.
