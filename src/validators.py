import pandas as pd

def validate_dataframe(df: pd.DataFrame, required_columns: list) -> bool:
    """Checks if the dataframe has the required columns and is not empty."""
    if df.empty:
        return False
    return all(col in df.columns for col in required_columns)
