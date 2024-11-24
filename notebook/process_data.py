# %%
import polars as pl
from IPython.display import display

from src.consts import ROOT

# %%
# データの確認とカテゴリごとにソートして保存するだけ
# %%
df = pl.read_csv(ROOT / "data" / "raw" / "products.csv").sort(
    by=["category", "small_category", "name", "url"]
)  # urlはuniqueなので順番一意に定まる
display(df)

# %%
# 具体小カテゴリの確認
print(len(list(df.filter(pl.col("small_category") == "パン・シリアル")["name"])))
print(list(df.filter(pl.col("small_category") == "パン・シリアル")["name"]))

# %%
print(df.columns)
# %%
df.describe()
# %%
# カテゴリ・小カテゴリの確認
print(list(df["category"].unique()))
print(list(df["small_category"].unique()))

# %%
# セブンプレミアムの確認
df.group_by("is_seven_premium").agg(pl.count())

# %%
df["name"].value_counts().sort("count", descending=True)  # 商品名に重複あり
# %%
df["name"].value_counts().sort("count", descending=True)
# %%
df.write_csv(ROOT / "data" / "processed" / "products.csv")
# %%
