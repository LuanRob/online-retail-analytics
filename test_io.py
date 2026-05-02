
print("INICIO")

from src.io_utils import load_raw_data

print("IMPORT OK")

df = load_raw_data()

print("LOAD OK")

print("Shape:", df.shape)