import pandas as pd
from pathlib import Path

from src.config import RAW_FILE


def load_raw_data() -> pd.DataFrame:
    """Lê o Excel original e concatena as abas em um único DataFrame."""
    sheets = pd.read_excel(RAW_FILE, sheet_name=None, engine="openpyxl")
    return pd.concat(sheets.values(), ignore_index=True)


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    """Salva DataFrame em parquet, criando o diretório se necessário."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)