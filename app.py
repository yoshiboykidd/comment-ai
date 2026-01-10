# 特徴キーワードの定義データ
cast_features = {
    "visual_systems": [
        "美人", "可愛い", "清楚", "正統派", "透明感", 
        "癒やし系", "アイドル系", "小動物系", "ギャル", 
        "派手", "地雷・量産型", "サブカル女子", "韓国風", 
        "ハーフ顔", "ボーイッシュ", "綺麗なお姉さん", 
        "女子アナ系", "モデル系"
    ],
    "attributes": [
        "現役感", "フレッシュ", "女子大生", "OL"
    ],
    "personalities": [
        "天真爛漫", "ノリが良い", "神対応", "聞き上手", 
        "おっとり", "真面目・一生懸命", "甘えん坊", 
        "人懐っこい", "小悪魔", "ツンデレ"
    ],
    "gap_elements": [
        "実はグラマラス", "マシュマロ肌・ボディ", "実は積極的"
    ]
}

# プロフィール文章生成のロジック例
def generate_profile_text(visual, attribute, personality, gap=None):
    """
    選択されたキーワードから紹介文のプロトタイプを生成する
    """
    intro = f"【{visual} × {attribute}】"
    body = f"圧倒的な{visual}のオーラを纏いつつ、{attribute}ならではの{personality}な一面が魅力です。"
    
    # ギャップ要素がある場合の処理（ネガティブ回避ロジック）
    if gap:
        if gap in ["実はグラマラス", "マシュマロ肌・ボディ"]:
            gap_text = f"一見すると{visual}でスレンダーな印象ですが、{gap}という最高のギャップを隠し持っています。"
        else:
            gap_text = f"普段は{personality}ですが、接客中は{gap}な姿を見せてくれることも…。"
        return f"{intro}\n{body}\n{gap_text}"
    
    return f"{intro}\n{body}"

# 実行例
profile = generate_profile_text(
    visual="清楚", 
    attribute="現役感", 
    personality="聞き上手", 
    gap="マシュマロ肌・ボディ"
)

print(profile)
