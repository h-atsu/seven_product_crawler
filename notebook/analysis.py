# %%
import polars as pl

from src.consts import ROOT

# %%
df = pl.read_csv(ROOT / "data" / "raw" / "products.csv")
df.head()

# %%
