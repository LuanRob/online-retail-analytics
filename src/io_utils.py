import pandas as pd
from pathlib import Path

from src.config import RAW_FILE


# ========================
# LOAD RAW DATA
# ========================
def load_raw_data() -> pd.DataFrame:
    """
    Lê o arquivo Excel original e concatena as abas.
    """
    sheets = pd.read_excel(RAW_FILE, sheet_name=None, engine="openpyxl")
    df = pd.concat(sheets.values(), ignore_index=True)

    return df

# Salvar parquet 
def load_parquet(df: pd.DataFrame, path: Path):
    """
    Salva arquivo Parquet e retorna um DataFrame.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


# Ler parquet
def load_parquet(path: Path) -> pd.DataFrame:
    """'
    Lê um arquivo Parquet e retorna um DataFrame.
    """
    return pd.read_parquet(path)