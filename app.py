import streamlit as st

# ページ基本設定
st.set_page_config(page_title="プロフィール自動生成ツール", layout="centered")

# カスタムCSSで見た目を調整（若い子店らしい清潔感）
st.markdown("""
    <style>
    .main { background-color: #fff5f8; }
    .stButton>button { background-color: #ff66a1; color: white; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💖 プロフィール作成ツール")

# --- 入力エリア ---
st.subheader("項目を選んでください")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("名前", "あみ")
    visual = st.selectbox("① 系統（見た目）", [
        "美人", "可愛い", "清楚", "正統派", "透明感", "癒し系", "アイドル系", 
        "小動物系", "ギャル", "派手", "地雷・量産型", "サブカル女子", 
        "韓国風", "ハーフ顔", "ボーイッシュ", "綺麗なお姉さん", "女子アナ系", "モデル系"
    ])

with col2:
    attr = st.selectbox("② 属性（現役感）", ["現役感", "フレッシュ", "女子大生", "OL"])
    personality = st.selectbox("③ 味付け（性格）", [
        "天真爛漫", "ノリが良い", "神対応", "聞き上手", "おっとり", 
        "真面目・一生懸命", "甘えん坊", "人懐っこい", "小悪魔", "ツンデレ"
    ])

gap = st.selectbox("④ ギャップ要素（秘密の魅力）", ["なし", "実はグラマラス", "マシュマロ肌・ボディ", "実は積極的"])

# --- 生成ロジック ---
def generate_profile():
    title = f"【{visual} × {attr}】{name}さん"
    
    # 基本紹介文
    intro = (
        f"圧倒的な「{visual}」のオーラを纏いつつ、{attr}ならではの初々しさと、"
        f"「{personality}」な一面を併せ持つ、今大注目の女の子です。\n\n"
        f"お話ししているだけで心が洗われるような「{visual}」の魅力はもちろん、"
        f"接客スタイルも非常に丁寧で{personality}なのが特徴です。"
    )

    # ギャップ要素の出し分け（ネガティブ回避）
    gap_text = ""
    if gap in ["実はグラマラス", "マシュマロ肌・ボディ"]:
        gap_text = (
            f"\n\n一見すると{visual}でスレンダーな印象を与えますが、"
            f"実は誰もが羨む「{gap}」を隠し持っているという、最高のギャップの持ち主でもあります。"
        )
    elif gap == "実は積極的":
        gap_text = (
            f"\n\n普段は{personality}で控えめな印象ですが、"
            f"二人きりになると「{gap}」な姿を見せてくれることも…。"
        )
    else:
        gap_text = f"\n\nその{attr}らしいフレッシュな魅力に、誰もが癒されること間違いありません。"

    return f"{title}\n\n{intro}{gap_text}"

# --- 出力エリア ---
st.markdown("---")
if st.button("紹介文を生成する"):
    result = generate_profile()
    st.text_area("生成結果（そのままコピー）", value=result, height=300)
    st.success("紹介文が完成しました！")
