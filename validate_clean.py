import pandas as pd

from src.config import CLEAN_DIR


transactions = pd.read_parquet(
    CLEAN_DIR / "transactions.parquet"
)

cancellations = pd.read_parquet(
    CLEAN_DIR / "cancellations.parquet"
)

adjustments = pd.read_parquet(
    CLEAN_DIR / "adjustments.parquet"
)


print("\n=== SHAPES ===")
print("Transactions:", transactions.shape)
print("Cancellations:", cancellations.shape)
print("Adjustments:", adjustments.shape)


print("\n=== NULLS ===")
print(transactions.isnull().sum())


print("\n=== INVALID CHECKS ===")

print(
    "Price <= 0:",
    (transactions["Price"] <= 0).sum()
)

print(
    "Quantity <= 0:",
    (transactions["Quantity"] <= 0).sum()
)

print(
    "Cancellation invoices:",
    transactions["Invoice"]
    .astype(str)
    .str.startswith("C")
    .sum()
)


print("\n=== REVENUE CHECK ===")

print(
    transactions["Revenue"]
    .describe()
)