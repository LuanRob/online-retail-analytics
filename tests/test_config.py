from pathlib import Path

from src import config

def test_base_dir_matches_project_root():
    expected_base_dir = Path(__file__).resolve().parent.parent
    assert config.BASE_DIR == expected_base_dir

def test_data_directories_are_derived_from_base_dir():
    assert config.DATA_DIR == config.BASE_DIR / "data"
    assert config.RAW_DIR == config.DATA_DIR / "raw"
    assert config.STAGING_DIR == config.DATA_DIR / "staging"
    assert config.CLEAN_DIR == config.DATA_DIR / "clean"
    assert config.ANALYTICS_DIR == config.DATA_DIR / "analytics"


def test_raw_file_points_to_expected_excel_file():
    assert config.RAW_FILE == config.RAW_DIR / "online_retail_II.xlsx"


def test_non_product_stockcodes_cover_expected_markers():
    expected_codes = {
        "POST", "DOT", "M", "C2", "D", "S", "PADS", "CRUK", "B", "GIFT", "C3"
    }
    assert config.NON_PRODUCT_STOCKCODES == expected_codes


def test_column_mapping_normalizes_customer_id():
    assert config.COLUMN_MAPPING == {"Customer ID": "CustomerID"}
