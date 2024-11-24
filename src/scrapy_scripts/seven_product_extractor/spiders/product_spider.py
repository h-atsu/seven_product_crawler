import re

import scrapy

from ..items import SevenProductItem


class SevenElevenSpider(scrapy.Spider):
    name = "seven_eleven"
    allowed_domains = ["sej.co.jp"]
    start_urls = ["https://www.sej.co.jp/products"]

    def parse(self, response):
        category_links = response.css(
            "#pbBlock3329311 ul.link-img-list li a::attr(href)"
        ).getall()

        for link in category_links:
            if link == "/products/a/7premium/":
                # seven premiumのカテゴリは他と異なるため特別処理
                links = [
                    "https://www.sej.co.jp/products/a/7premium/daily_dish/",
                    "https://www.sej.co.jp/products/a/7premium/fresh/",
                    "https://www.sej.co.jp/products/a/7premium/process/",
                    "https://www.sej.co.jp/products/a/7premium/bread/",
                    "https://www.sej.co.jp/products/a/7premium/confectionery/",
                    "https://www.sej.co.jp/products/a/7premium/sweets_ice_cream/",
                    "https://www.sej.co.jp/products/a/7premium/frozen_foods/",
                    "https://www.sej.co.jp/products/a/7premium/dairy/",
                    "https://www.sej.co.jp/products/a/7premium/drink/",
                    "https://www.sej.co.jp/products/a/7premium/alcohol/",
                ]
                for link in links:
                    yield response.follow(
                        link, self.parse_category, cb_kwargs={"is_seven_premium": True}
                    )
            else:
                yield response.follow(
                    link, self.parse_category, cb_kwargs={"is_seven_premium": False}
                )

    def parse_category(self, response, is_seven_premium):
        # カテゴリページの場合
        category = response.css("div.pbBlock h1::text").get().strip()
        lineup_links = response.css(
            'a:contains("のラインナップを見る")::attr(href)'
        ).getall()

        if lineup_links:
            # 各サブカテゴリの商品一覧ページをクロール
            for link in lineup_links:
                yield response.follow(
                    link,
                    self.parse_product_list,
                    cb_kwargs={
                        "is_seven_premium": is_seven_premium,
                        "category": category,
                    },
                )
        else:
            # 商品一覧ページの場合は直接parse_product_listを呼び出す
            yield from self.parse_product_list(
                response, is_seven_premium=is_seven_premium, category=category
            )

    def parse_product_list(self, response, is_seven_premium, category):
        # 商品リンクの取得
        product_links = response.css(
            "a[href*='/products/a/item/']:has(img)::attr(href)"
        ).getall()

        small_catgory_text = response.css("h1::text").get()
        small_category = small_catgory_text.strip() if small_catgory_text else ""

        # 商品詳細ページへ遷移
        for link in product_links:
            yield response.follow(
                link,
                self.parse_product,
                cb_kwargs={
                    "is_seven_premium": is_seven_premium,
                    "category": category,
                    "small_category": small_category,
                },
            )

        # ページネーションの処理
        next_page = response.css('a:contains("［次へ］")::attr(href)').get()
        if next_page:
            yield response.follow(
                next_page,
                self.parse_product_list,
                cb_kwargs={"is_seven_premium": is_seven_premium, "category": category},
            )

    def parse_product(self, response, is_seven_premium, category, small_category):
        item = SevenProductItem()

        # 商品基本情報の取得
        item["name"] = response.css("h1::text").get().strip().replace("　", "")
        item["is_seven_premium"] = is_seven_premium
        item["category"] = category
        item["small_category"] = small_category
        item["url"] = response.url

        # 商品画像URLの取得 TODO: 複数画像のカルーセルに対応(https://www.sej.co.jp/products/a/item/302715/)
        item["image_url"] = response.css("div.productWrap img::attr(src)").get()

        # 商品説明の取得（div.item_text内のテキスト）
        description_text = response.css("div.item_text p::text").get()
        description = description_text.strip() if description_text else ""
        item["description"] = description

        # 価格情報の取得（div.item_price内のテキスト）
        price_text = response.css("div.item_price p::text").get()
        if price_text:
            # カンマを含む数値に対応した正規表現パターン
            pattern_tax_included = r"税込([\d,]+(?:\.\d+)?)円"
            pattern_tax_excluded = r"([\d,]+(?:\.\d+)?)円"

            # 税込価格の抽出とカンマの除去
            tax_included_match = re.search(pattern_tax_included, price_text)
            if tax_included_match:
                item["price_tax"] = float(tax_included_match.group(1).replace(",", ""))

            # 税抜価格の抽出とカンマの除去
            tax_excluded_match = re.search(pattern_tax_excluded, price_text)
            if tax_excluded_match:
                item["price"] = float(tax_excluded_match.group(1).replace(",", ""))

        # アレルギー情報の取得（テーブルから）
        allergens_text = response.xpath(
            '//th[contains(text(), "アレルギー")]/following-sibling::td//dd/text()'
        ).getall()
        allergens_list = []
        for s in allergens_text:
            for allergen in s.strip().split("・"):
                if allergen == "なし":
                    continue
                allergens_list.append(allergen)

        item["allergens"] = allergens_list

        # 栄養成分情報の取得（テーブルから）
        nutrition = response.xpath(
            '//th[contains(text(), "栄養成分")]/following-sibling::td/text()'
        ).get()
        if nutrition:
            # 正規表現パターンを定義
            patterns = {
                "calories": r"熱量：(\d+\.?\d*)kcal",
                "protein": r"たんぱく質：(\d+\.?\d*)g",
                "fat": r"脂質：(\d+\.?\d*)g",
                "carbohydrate": r"炭水化物：(\d+\.?\d*)g",
                "sugar": r"糖質：(\d+\.?\d*)g",
                "fiber": r"食物繊維：(\d+\.?\d*)g",
                "salt": r"食塩相当量：(\d+\.?\d*)g",
            }

            # 各栄養成分を個別に抽出
            for key, pattern in patterns.items():
                match = re.search(pattern, nutrition)
                if match:
                    item[key] = float(match.group(1))

        print(item)
        yield item
