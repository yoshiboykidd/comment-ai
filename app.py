import streamlit as st

# ページ基本設定
st.set_page_config(page_title="キャストプロフィール作成", layout="wide")

st.title("💖 プロフィール作成（全項目表示・チェックボックス版）")

# --- レイアウト：左側に数値、右側にチェックボックス ---
col_spec, col_tags = st.columns([1, 2])

with col_spec:
    st.subheader("📊 基本スペック")
    name = st.text_input("名前", "あみ")
    age = st.number_input("年齢", 18, 35, 20)
    height = st.number_input("身長 (cm)", 140, 180, 158)
    
    st.write("3サイズ / カップ")
    c1, c2, c3, c4 = st.columns(4)
    with c1: b = st.number_input("B", value=85)
    with c2: w = st.number_input("W", value=58)
    with c3: h = st.number_input("H", value=86)
    with c4: cup = st.selectbox("Cup", ["A","B","C","D","E","F","G","H以上"])

with col_tags:
    st.subheader("🏷️ 特徴キーワード（複数選択可）")
    
    # 1. 系統（ビジュアル）
    st.write("**【系統・ビジュアル】**")
    v_list = [
        "美人", "可愛い", "清楚", "正統派", "透明感", "癒し系", "アイドル系", 
        "小動物系", "ギャル", "派手", "地雷・量産型", "サブカル女子", 
        "韓国風", "ハーフ顔", "ボーイッシュ", "綺麗なお姉さん", "女子アナ系", "モデル系"
    ]
    # 3列でチェックボックスを並べる
    v_cols = st.columns(3)
    selected_visuals = [v for i, v in enumerate(v_list) if v_cols[i % 3].checkbox(v)]

    st.markdown("---")
    
    # 2. 属性 & 3. 味付け
    col_a, col_p = st.columns(2)
    with col_a:
        st.write("**【属性】**")
        a_list = ["現役感", "フレッシュ", "女子大生", "OL"]
        selected_attrs = [a for a in a_list if st.checkbox(a)]
        
    with col_p:
        st.write("**【味付け・接客】**")
        p_list = ["天真爛漫", "ノリが良い", "神対応", "聞き上手", "おっとり", "一生懸命", "甘えん坊", "人懐っこい", "小悪魔", "ツンデレ"]
        selected_personalities = [p for p in p_list if st.checkbox(p)]

    st.markdown("---")
    
    # 4. ギャップ要素
    st.write("**【秘密のギャップ】** ※ポジティブ表現に変換されます")
    g_list = ["実はグラマラス", "マシュマロ肌・ボディ", "実は積極的"]
    selected_gaps = [g for g in g_list if st.checkbox(g)]

# --- 生成ロジック ---
def generate_text():
    # ヘッダー・スペック
    res = f"【{'/'.join(selected_visuals) if selected_visuals else '注目キャスト'}】{name} ({age})\n"
    res += f"T{height} / B{b}({cup}) / W{w} / H{h}\n"
    res += "----------------------------\n\n"
    
    # 本文（選択されたキーワードを文章に組み込む）
    v_str = "・".join(selected_visuals) if selected_visuals else "抜群のビジュアル"
    a_str = "・".join(selected_attrs) if selected_attrs else "フレッシュ"
    p_str = "・".join(selected_personalities) if selected_personalities else "誠実"
    
    res += f"圧倒的な「{v_str}」の魅力を放ち、{a_str}ならではの初々しさと「{p_str}」な一面を併せ持つ女の子です。\n\n"
    
    # ギャップの処理
    if selected_gaps:
        for g in selected_gaps:
            if "グラマラス" in g or "マシュマロ" in g:
                res += f"一見するとスレンダーな印象ですが、実は誰もが羨む「{g}」を隠し持っているという、最高のギャップの持ち主でもあります。\n\n"
            elif "積極的" in g:
                res += f"普段は控えめな印象ですが、二人きりになると「{g}」な姿を見せてくれることも…。\n\n"
    
    res += "ぜひ一度、彼女のフレッシュな魅力に癒されてみてください。"
    return res

# --- 出力エリア ---
st.markdown("---")
if st.button("✨ この内容で紹介文を生成する"):
    if not selected_visuals:
        st.warning("系統を1つ以上選んでください")
    else:
        result = generate_text()
        st.text_area("生成結果", value=result, height=400)
