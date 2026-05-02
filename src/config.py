from pathlib import Path

# ========================
# BASE PATH
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# DATA PATHS
# ========================
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
CLEAN_DIR = DATA_DIR / "clean"
ANALYTICS_DIR = DATA_DIR / "analytics"

# ========================
# RAW FILE
# ========================
RAW_FILE = RAW_DIR / "online_retail_II.xlsx"

# ========================
# NON-PRODUCT STOCKCODES
# ========================
NON_PRODUCT_STOCKCODES = {
    "POST", "DOT", "M", "C2", "D", "S", "PADS", "CRUK", "B", "GIFT", "C3"
}

# ========================
# COLUMN MAPPING
# ========================
COLUMN_MAPPING = {
    "Customer ID": "CustomerID"
}