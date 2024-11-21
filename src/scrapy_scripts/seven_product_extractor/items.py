from scrapy import Field, Item


class SevenProductItem(Item):
    name = Field()  # 商品名
    price = Field()  # 価格（税抜）
    price_tax = Field()  # 価格（税込）
    description = Field()  # 商品説明
    region = Field()  # 販売地域
    allergens = Field()  # アレルギー物質
    calories = Field()  # 熱量
    carbohydrate = Field()  # 炭水化物
    fat = Field()  # 脂質
    fiber = Field()  # 食物繊維
    protein = Field()  # たんぱく質
    salt = Field()  # 食塩相当量
    sugar = Field()  # 糖質
    category = Field()  # 大カテゴリ
    small_category = Field()  # 小カテゴリ
    url = Field()  # 商品URL
    image_url = Field()  # 商品画像URL
