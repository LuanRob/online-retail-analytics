# imports
import pandas as pd

from src.config import ANALYTICS_DIR, CLEAN_DIR
from src.io_utils import save_parquet

# Carregando dados
def load_transaction() -> pd.DataFrame:
    
    df = pd.read_parquet(
        CLEAN_DIR / "transactions.parquet"
    )
    return df

# Filtrar clientes validos
def filter_valid_customers(
        df: pd.DataFrame
) -> pd.DataFrame:
    
    df = df[
        df["CustomerID"].notna(
        )
    ].copy()
    return df

# Snapshot date
def get_snapshot_date(
        df: pd.DataFrame
):
    
    snapshot_date = (
        df["InvoiceDate"].max()
        + pd.Timedelta(days=1)
    )

    return snapshot_date

# Calcular RFM
def calculate_rfm(
        df: pd.DataFrame,
        snapshot_date

) -> pd.DataFrame:

    rfm = (
        df.groupby("CustomerID")
        .agg({
            "InvoiceDate": lambda x:
                (snapshot_date - x.max()).days,
            "Invoice": "nunique",
            "Revenue": "sum"  
        })
        .reset_index()
    )

    rfm.columns = ["CustomerID", "Recency", "Frequency", "Monetary"]

    return rfm

# Scoring RFM
def create_rfm_score(
        rfm: pd.DataFrame
) -> pd.DataFrame:
    
    # Recency: menor é melhor
    rfm["R_score"] = pd.qcut(
        rfm["Recency"],
        5,
        labels=[5,4,3,2,1]
    )

    # Frequency: maior é melhor
    rfm["F_score"] = pd.qcut(
        rfm["Frequency"]
        .rank(method="first"),
        5,
        labels=[1,2,3,4,5]
    )

    # Monetary: maior é melhor
    rfm["M_score"] = pd.qcut(
        rfm["Monetary"],
        5,
        labels=[1,2,3,4,5]
    )

    return rfm

# Criar RFM score
def create_rfm_segment(
        rfm: pd.DataFrame
) -> pd.DataFrame:
    
    rfm["RFM_score"] = (
        rfm["R_score"].astype(str)
        + rfm["F_score"].astype(str)
        + rfm["M_score"].astype(str)
    )

    return rfm

# Segmentação de degocios
def assign_segments(
        rfm: pd.DataFrame
) -> pd.DataFrame:
    
    def segment(row):
        r = int(row["R_score"])
        f = int(row["F_score"])
        
        if r >= 4 and f >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 4:
            return "Recent Customers"
        elif f >= 4:
            return "Frequent Customers"
        else:
            return "Others"
        
    rfm["Segment"] = rfm.apply(segment, axis=1)
    return rfm

# Salvando parquet
def save_rfm(
        rfm: pd.DataFrame
):
    save_parquet(
        rfm,
        ANALYTICS_DIR / "rfm.parquet"
    )

# Pepiline principal
def main():

    print("Loading transaction...")
    df = load_transaction()

    print("Filtering customers...")
    df = filter_valid_customers(df)

    print("Creating snapshot date...")
    snapshot_date = get_snapshot_date(df)

    print("Calculating RFM...")
    rfm = calculate_rfm(df, snapshot_date)

    print("Creating score...")
    rfm = create_rfm_score(rfm)

    print("Creating RFM segment...")
    rfm = create_rfm_segment(rfm)

    print("Assingning custormer segments...")
    rfm = assign_segments(rfm)

    print("Saving RFM...")
    save_rfm(rfm)

    print("RFM pipeline completed.")

if __name__ == "__main__":
    main()
