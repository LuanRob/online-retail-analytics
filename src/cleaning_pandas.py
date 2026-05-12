# Imports e setup

import pandas as pd

from src.config import (
    CLEAN_DIR,
    NON_PRODUCT_STOCKCODES,
    COLUMN_MAPPING
)

from src.io_utils import (
    load_raw_data,
    save_parquet
)

# Criando função de limpeza
def normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padronizando colunas e strings.
    """
    # Renomear as colunas
    df = df.rename(columns=COLUMN_MAPPING)
    # Trim as strings
    df['Invoice'] = df['Invoice'].astype(str).str.strip()

    df["StockCode"] = (
        df["StockCode"]
        .astype(str)
        .str.strip()
        .str.upper()

    )

    df["Description"] = (
        df["Description"]
        .str.strip()
    )
    return df

# Deduplicação 
def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicadas exatas
    """

    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    print(f"Duplicatas removidas: {before - after}")
    return df

# Separar adjustments
def split_adjustments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Separar stockodes não-produto.
    """

    mask = df["StockCode"].isin(NON_PRODUCT_STOCKCODES)
    adjustments = df[mask].copy()
    transcations = df[~mask].copy()
    print(f"adjustments: {len(adjustments)}:,")

    return transcations, adjustments

# Separar cancelamentos
def split_cancellations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Separar Invoices de cancelamento.
    """
    mask = df["Invoice"].str.startswith("C", na=False)
    cancellations = df[mask].copy()
    transactions = df[~mask].copy()
    print(f"Cancelamentos: {len(cancellations)}")

    return transactions, cancellations

# Limpeza final de transações
def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mantem apenas transações validas.
    """
    before = len(df)
    df = df[
        (df["Price"] > 0) 
        & (df["Quantity"] > 0)
        & (df["Description"].notna())
    ].copy()
    after = len(df)
    print(f"Transações inválidas removidas: {before - after}")
    return df

# Enriquecimento de dados
def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Criar colunas derivadas
    """
    df["Revenue"] = df["Quantity"] * df["Price"]
    
    df["InvoiceYearMonth"] = (
        df["InvoiceDate"]
        .dt.to_period("M")
        .astype(str)
    )

    df["CustomerIDFlag"] = (
        df["CustomerID"]
        .notna()
    )

    return df

def main():

    print("Loading raw data...")
    df = load_raw_data()

    print("Normalizing...")
    df = normalize_data(df)

    print("Removing duplicates...")
    df = remove_duplicates(df)

    print("Splitting adjustments...")
    df, adjustments = split_adjustments(df)

    print("Splitting cancellations...")
    df, cancellations = split_cancellations(df)

    print("Cleaning transactions...")
    transactions = clean_transactions(df)

    print("Enriching transactions...")
    transactions = enrich_data(transactions)

    # ========================
    # SAVE FILES
    # ========================

    save_parquet(
        transactions,
        CLEAN_DIR / "transactions.parquet"
    )

    save_parquet(
        cancellations,
        CLEAN_DIR / "cancellations.parquet"
    )

    save_parquet(
        adjustments,
        CLEAN_DIR / "adjustments.parquet"
    )

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
