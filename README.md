# 実行方法

uv でパッケージ管理を行うためまず下記コマンドを実行

```
uv sync
```

続いて，プロジェクトルートディレクトリにて以下のコマンドを実行して商品データを取得

```
cd src/scrapy_scripts
scrapy crawl seven_eleven -o ../../data/raw/products.csv
```
