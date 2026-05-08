import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DIMENSIONS_DIR = DATA_DIR / "dimensions"
FACTS_DIR = DATA_DIR / "facts"
LOGS_DIR = DATA_DIR / "logs"
SQL_DIR = BASE_DIR / "sql"

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, DIMENSIONS_DIR, FACTS_DIR, LOGS_DIR, SQL_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Configuration
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://v3.football.api-sports.io")
REQUEST_DELAY = int(os.getenv("REQUEST_DELAY", 2))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
TIMEOUT = int(os.getenv("TIMEOUT", 30))

# Pipeline Configuration
LEAGUE_ID = int(os.getenv("LEAGUE_ID", 71))
SEASON = int(os.getenv("SEASON", 2024))
FIXTURE_LIMIT = int(os.getenv("FIXTURE_LIMIT", 20))        # partidas com detalhes (stats/eventos/escalações)
FIXTURE_PLAYER_LIMIT = int(os.getenv("FIXTURE_PLAYER_LIMIT", 5))  # partidas com stats individuais de jogadores
TEAM_STATS_LIMIT = int(os.getenv("TEAM_STATS_LIMIT", 5))   # times com elenco/técnico/estatísticas
MAX_DAILY_REQUESTS = int(os.getenv("MAX_DAILY_REQUESTS", 100))
