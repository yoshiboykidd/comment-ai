import streamlit as st

# 1. ページ基本設定
st.set_page_config(page_title="プロライター仕様：プロフィール生成ツール", layout="wide")

# カスタムCSS（デザイン性を高める）
st.markdown("""
    <style>
    .main { background-color: #fdfafb; }
    .stButton>button { background-color: #d63384; color: white; border-radius: 5px; width: 100%; font-weight: bold; }
    .report-text { background-color: #ffffff; padding: 20px; border: 1px solid #ffcce0; border-radius: 10px; line-height: 1.8; color: #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🖋️ オナクラ専門プロライター：プロフィール自動作成")

# 2. 入力エリア：左側にスペック、右側にキーワード
col_spec, col_tags = st.columns([1, 2])

with col_spec:
    st.subheader("📊 キャストスペック")
    name = st.text_input("名前", "あみ")
    age = st.number_input("年齢", 18, 35, 20)
    height = st.number_input("身長 (cm)", 140, 180, 158)
    
    st.write("3サイズ / カップ")
    c1, c2, c3, c4 = st.columns(4)
    with c1: b = st.number_input("B", value=85)
    with c2: w = st.number_input("W", value=58)
    with c3: h = st.number_input("H", value=86)
    with c4: cup = st.selectbox("Cup", ["A","B","C","D","E","F","G","H以上"])
    
    st.markdown("---")
    # 文字数調整スライダー（デフォルト400字）
    target_length = st.slider("目標文字数（本文）", 200, 800, 400, step=50)

with col_tags:
    st.subheader("🏷️ 特徴・属性（全表示チェックボックス）")
    
    # 系統（ビジュアル）
    st.write("**【系統・ビジュアル】**")
    v_list = ["美人", "可愛い", "清楚", "正統派", "透明感", "癒し系", "アイドル系", "小動物系", "ギャル", "派手", "地雷・量産型", "サブカル女子", "韓国風", "ハーフ顔", "ボーイッシュ", "綺麗なお姉さん", "女子アナ系", "モデル系"]
    v_cols = st.columns(4)
    selected_visuals = [v for i, v in enumerate(v_list) if v_cols[i % 4].checkbox(v)]

    # 属性・味付け・ギャップ（全表示）
    col_a, col_p, col_g = st.columns(3)
    with col_a:
        st.write("**【属性】**")
        a_list = ["現役感", "フレッシュ", "女子大生", "OL"]
        selected_attrs = [a for a in a_list if st.checkbox(a)]
    with col_p:
        st.write("**【味付け・接客】**")
        p_list = ["天真爛漫", "ノリが良い", "神対応", "聞き上手", "おっとり", "一生懸命", "甘えん坊", "人懐っこい", "小悪魔", "ツンデレ"]
        selected_personalities = [p for p in p_list if st.checkbox(p)]
    with col_g:
        st.write("**【秘密のギャップ】**")
        g_list = ["実はグラマラス", "マシュマロ肌・ボディ", "実は積極的"]
        selected_gaps = [g for g in g_list if st.checkbox(g)]

# 3. プロライター文章生成ロジック
def generate_pro_writing():
    v_str = "・".join(selected_visuals) if selected_visuals else "至極の美女"
    a_str = "・".join(selected_attrs) if selected_attrs else "期待の新星"
    p_str = "・".join(selected_personalities) if selected_personalities else "癒やしの接客"
    
    # --- 3行アイキャッチコピー ---
    catch_1 = f"《{v_str}》を体現する、{a_str}だけの奇跡の透明感。"
    catch_2 = f"{p_str}で包み込む、あなただけの極上プライベートタイム。"
    if selected_gaps:
        catch_3 = f"魅惑の「{selected_gaps[0]}」に溺れる、至福のギャップ体験。"
    else:
        catch_3 = f"T{height}・{cup}カップの美ラインが描く、官能のシルエット。"
    eyecatch = f"◆{catch_1}\n◆{catch_2}\n◆{catch_3}"

    # --- 情緒的な本文 ---
    intro = f"都会の喧騒を忘れさせるほどの圧倒的な「{v_str}」を纏い、当店に舞い降りた{a_str}の{name}さん。一目見た瞬間に吸い込まれるような瞳と、{height}cmの端正な立ち姿は、まさに理想を形にしたかのようです。"
    
    middle = f"\n\n彼女の最大の魅力は、その美貌以上に「{p_str}」な内面。聞き上手で人懐っこい彼女との時間は、心の奥底から解きほぐされるような至福のひとときをお約束します。"
    
    spec_info = f"\n\nそして、特筆すべきはそのスタイル。B{b}({cup})・W{w}・H{h}という曲線美は、視覚だけでなく、実際に触れることでその真価を発揮します。"
    
    gap_detail = ""
    if any(g in selected_gaps for g in ["実はグラマラス", "マシュマロ肌・ボディ"]):
        gap_detail = f"\n\n「{selected_gaps[0]}」という言葉がこれほど似合う子は他にいません。清楚な見た目からは想像もつかない、柔らかく瑞々しい質感に、あなたの理性が崩れ去るのも時間の問題です。"
    else:
        gap_detail = "\n\n若さ溢れる弾力と、丁寧に手入れされた素肌の質感。指先が触れるたびに伝わる温度に、身も心も熱くなるのを感じるはずです。"
    
    closing = f"\n\n{name}さんが織りなす「{a_str}」ならではのフレッシュで濃密な時間を、ぜひお楽しみください。"

    full_body = intro + middle + spec_info + gap_detail + closing
    
    # 文字数調整
    if len(full_body) > target_length:
        full_body = full_body[:target_length] + "..."
        
    return eyecatch, full_body

# 4. 出力エリア
st.markdown("---")
if st.button("🖋️ プロライターの視点で紹介文を書き上げる"):
    if not selected_visuals:
        st.error("※系統を1つ以上選択してください。")
    else:
        eyecatch, body = generate_pro_writing()
        
        # スペック表示
        st.code(f"【{selected_visuals[0]} / {selected_attrs[0] if selected_attrs else '新人'}】 {name} ({age})\n"
                f"T{height} / B{b}({cup}) / W{w} / H{h}")
        
        st.info(f"📸 **アイキャッチコピー**\n\n{eyecatch}")
        st.markdown(f'<div class="report-text"><b>📝 本文</b>（約{len(body)}文字）<br><br>{body}</div>', unsafe_allow_html=True)
        
        # コピー用
        st.subheader("📋 コピー用テキスト")
        st.text_area("そのままSNSやサイトへ", value=f"{eyecatch}\n\n{body}", height=300)
