# %%
import polars as pl
from IPython.display import display

from src.consts import ROOT

# %%
pl.Config.set_tbl_cols(50)
pl.Config.set_tbl_rows(50)

# %%
# データの確認とカテゴリごとにソートして保存する
# %%
df = pl.read_csv(ROOT / "data" / "raw" / "products.csv").sort(
    by=["category", "small_category", "name", "url"]
)  # urlはuniqueなので順番一意に定まる
display(df.head())


# %%
display(df.describe())
# %%
# カテゴリ・小カテゴリの確認
display(df.group_by("category").agg(pl.count()))
display(df.group_by(["category", "small_category"]).agg(pl.count()))


# %%
# セブンプレミアムの確認
display(df.group_by("is_seven_premium").agg(pl.count()))

# %%
df["name"].value_counts().sort("count", descending=True)  # 商品名に重複あり
# %%
df = df.unique(
    subset=["name"]
)  # 販売地域ごとに商品があり重複があるが地域差は一旦潰す TODO: 地域情報も取得
# %%
df["name"].value_counts().sort("count", descending=True)
# %%
df.write_csv(ROOT / "data" / "processed" / "products.csv")
# %%
