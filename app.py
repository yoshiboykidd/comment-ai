import streamlit as st
import pandas as pd
from openai import OpenAI

# ==========================================
# 1. 設定：スプレッドシートIDを適用済み
# ==========================================
SPREADSHEET_ID = "1sIr-8ys0jSapzIlt8RSei4lYIKPbFdZjm5OofizxmYM"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"

# OpenAIクライアントの初期化
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 画面設定 ---
st.set_page_config(page_title="かりんと流・プロフ生成ツール", page_icon="✨", layout="centered")

# デザインの微調整
st.markdown("""
    <style>
    .main { background-color: #fffafb; }
    .stButton>button { 
        width: 100%; 
        border-radius: 20px; 
        background-color: #ff4b6e; 
        color: white; 
        font-weight: bold; 
        height: 3.5em;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff2a51;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ かりんと流・プロフ生成ツール")
st.caption("スプレッドシートの知能を使い、名前を出さずに『彼女』の魅力を最大化します")

# --- データの読み込み ---
@st.cache_data(ttl=600)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        return data
    except Exception as e:
        st.error("スプレッドシートの読み込みに失敗しました。共有設定が『リンクを知っている全員』になっているか確認してください。")
        return None

df = load_data()

if df is not None:
    # --- サイドバー：入力フォーム ---
    with st.sidebar:
        st.header("👤 キャスト基本情報")
        # 名前は入力しますが、AIへの命令で「本文には出さない」と封印します
        name_admin = st.text_input("キャスト名（管理用）", placeholder="例：あやか")
        age = st.number_input("年齢", min_value=18, max_value=60, value=20)
        
        st.subheader("📏 サイズ")
        c1, c2 = st.columns(2)
        with c1:
            height = st.number_input("身長", value=158)
            bust = st.number_input("バスト", value=85)
        with c2:
            cup = st.selectbox("カップ", ["A", "B", "C", "D", "E", "F", "G", "H", "I"], index=3)
            waist = st.number_input("ウエスト", value=58)
        hip = st.number_input("ヒップ", value=85)

        st.divider()
        
        st.header("🎨 キャラクター設定")
        # 【修正】系統は現場で迷わない5つに絞り込み
        display_types = ["清楚・癒やし", "モデル・上品", "妹・アイドル", "ギャル・小悪魔", "熟女・お姉さん"]
        selected_type = st.selectbox("基本系統（お手本の選択）", display_types)
        
        # 【修正】特徴キーワードは「多いまま」で現場のこだわりを反映
        keywords = st.multiselect(
            "特徴キーワード（複数選択）", 
            ["清楚", "癒やし", "S感", "ギャル", "妹系", "未経験", "笑顔", "脚線美", "モデル体型", 
             "高身長", "小柄", "色白", "豊満", "スレンダー", "人妻風", "JD", "ハーフ顔", "愛嬌", 
             "しっとり", "聞き上手", "美乳", "美肌", "モチモチ肌", "おっとり", "活発"]
        )

    # --- メイン処理 ---
    if st.button("かりんと流でプロフを生成する"):
        if not name_admin:
            st.warning("キャストの名前を入力してください（管理用）")
        else:
            with st.spinner("スプレッドシートから最適な文章を学習中..."):
                # 1. お手本の抽出（選択された系統の文字が含まれる行を探す）
                search_word = selected_type.split('・')[0] 
                relevant_samples = df[df["系統"].str.contains(search_word, na=False)]
                
                if len(relevant_samples) > 0:
                    samples = relevant_samples.sample(n=min(3, len(relevant_samples)))
                    sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in samples["かりんと流プロフ全文"]])
                else:
                    samples = df.sample(n=3)
                    sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in samples["かりんと流プロフ全文"]])

                # 2. プロンプト（名前使用禁止・彼女統一を強化）
                system_prompt = "貴方はメンズエステ業界の伝説的なライターです。気品、官能、期待感を完璧に調和させた文章を書きます。"
                
                user_prompt = f"""
以下のキャスト情報を元に、高級メンズエステのプロフィールを執筆してください。
提示した「お手本」の文章スタイルを継承しつつ、以下の【鉄の掟】を必ず守ってください。

### キャスト情報
年齢：{age}歳
サイズ：T{height} / B{bust}({cup}) / W{waist} / H{hip}
キーワード：{", ".join(keywords)}

### かりんと流・鉄の掟（絶対遵守）
1. 冒頭に【】で囲ったキャッチコピーを必ず「3行」作成すること。
2. 文中にキャストの名前（{name_admin}）は「絶対に」出さないこと。
3. キャストのことは、一貫して「彼女」と呼ぶこと。
4. 一人称（私、僕など）は使用禁止。
5. 二人称は「貴方」または「貴男」。
6. 「昼」「夜」「朝」「深夜」などの時間表現は、24時間営業のため「絶対に」使わないこと。
7. 「彼」という言葉は使わず「貴方」を使うこと。
8. 文章の最後は、読み手の期待感を最高潮に高め、予約へと誘う最高の一文で締めること。

### 参考にする文章スタイル（お手本）
{sample_texts}

作成された文章：
"""

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.75
                    )
                    
                    result_text = response.choices[0].message.content

                    # --- 結果表示 ---
                    st.subheader(f"✨ {name_admin} さんのプロフ案")
                    st.text_area("コピーして使用してください", result_text, height=600)
                    st.success("「彼女」で統一されたプロフが完成しました。")
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
else:
    st.info("スプレッドシートIDを確認してください。")
