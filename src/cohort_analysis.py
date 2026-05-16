import pandas as pd

from src.config import ANALYTICS_DIR, CLEAN_DIR
from src.io_utils import save_parquet


def load_transactions() -> pd.DataFrame:
    """Load cleaned transactions."""
    return pd.read_parquet(CLEAN_DIR / "transactions.parquet")


def filter_valid_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only transactions linked to identified customers."""
    return df[df["CustomerID"].notna()].copy()


def add_invoice_month(df: pd.DataFrame) -> pd.DataFrame:
    """Create a month-level transaction date."""
    df = df.copy()
    df["InvoiceMonth"] = (
        df["InvoiceDate"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )
    return df


def add_cohort_month(df: pd.DataFrame) -> pd.DataFrame:
    """Create the first purchase month for each customer."""
    df = df.copy()
    df["CohortMonth"] = df.groupby("CustomerID")["InvoiceMonth"].transform("min")
    return df


def add_period_number(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate how many months after the cohort month each purchase happened."""
    df = df.copy()

    invoice_year = df["InvoiceMonth"].dt.year
    invoice_month = df["InvoiceMonth"].dt.month
    cohort_year = df["CohortMonth"].dt.year
    cohort_month = df["CohortMonth"].dt.month

    df["PeriodNumber"] = (
        (invoice_year - cohort_year) * 12
        + (invoice_month - cohort_month)
        + 1
    )

    return df


def calculate_cohort_retention(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate active customers and retention rate by cohort period."""
    cohort = (
        df.groupby(["CohortMonth", "PeriodNumber"])["CustomerID"]
        .nunique()
        .reset_index(name="CustomersActive")
    )

    cohort_size = (
        cohort[cohort["PeriodNumber"] == 1][["CohortMonth", "CustomersActive"]]
        .rename(columns={"CustomersActive": "CohortSize"})
    )

    cohort = cohort.merge(cohort_size, on="CohortMonth", how="left")
    cohort["RetentionRate"] = cohort["CustomersActive"] / cohort["CohortSize"]

    return (
        cohort[["CohortMonth", "PeriodNumber", "CustomersActive", "RetentionRate"]]
        .sort_values(["CohortMonth", "PeriodNumber"])
        .reset_index(drop=True)
    )


def save_cohort(cohort: pd.DataFrame) -> None:
    save_parquet(
        cohort,
        ANALYTICS_DIR / "cohort.parquet"
    )


def main() -> None:
    print("Loading transactions...")
    df = load_transactions()

    print("Filtering valid customers...")
    df = filter_valid_customers(df)

    print("Creating invoice months...")
    df = add_invoice_month(df)

    print("Creating cohort months...")
    df = add_cohort_month(df)

    print("Calculating period numbers...")
    df = add_period_number(df)

    print("Calculating cohort retention...")
    cohort = calculate_cohort_retention(df)

    print("Saving cohort...")
    save_cohort(cohort)

    print("Cohort pipeline completed.")


if __name__ == "__main__":
    main()
