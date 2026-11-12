import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')

def database_url():
    directory = Path(os.getenv('TECM_DATA_DIR', str(ROOT / 'data'))).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    return os.getenv('TECM_DATABASE_URL', 'sqlite:///' + (directory / 'tecm.db').as_posix())

TIMEZONE = 'Africa/Nairobi'
SESSION_IDLE_SECONDS = 1800
SESSION_MAX_SECONDS = 28800
