import pandas as pd
from pathlib import Path

class Loader:
    def __init__(self, logger):
        self.logger = logger

    def save_to_csv(self, df: pd.DataFrame, path: Path):
        """Saves a DataFrame to CSV, creating directories if needed."""
        if df.empty:
            self.logger.warning(f"DataFrame is empty. Skipping save to {path.name}")
            return
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(path, index=False, encoding='utf-8')
            self.logger.info(f"Successfully saved: {path.name}")
        except Exception as e:
            self.logger.error(f"Failed to save {path.name}: {e}")
