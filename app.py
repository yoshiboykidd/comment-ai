import streamlit as st
import pandas as pd
from openai import OpenAI

# ==========================================
# 1. 設定：ご自身のスプレッドシートIDをここに入れてください
# ==========================================
SPREADSHEET_ID = "1sIr-8ys0jSapzIlt8RSei4lYIKPbFdZjm5OofizxmYM"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 画面設定 ---
st.set_page_config(page_title="かりんと流・プロフ生成ツール", page_icon="✨", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #fff5f7; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff4b6e; color: white; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ かりんと流・プロフ生成ツール")

# --- データの読み込み ---
@st.cache_data(ttl=600)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        return data
    except Exception as e:
        st.error("データの読み込みに失敗しました。スプレッドシートの共有設定を確認してください。")
        return None

df = load_data()

if df is not None:
    # --- サイドバー：入力フォーム ---
    with st.sidebar:
        st.header("👤 キャスト基本情報")
        name = st.text_input("名前（管理用・生成には使いません）", placeholder="例：あやか")
        age = st.number_input("年齢", min_value=18, max_value=60, value=20)
        
        st.subheader("📏 サイズ")
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("身長", value=158)
            bust = st.number_input("バスト", value=85)
        with col2:
            cup = st.selectbox("カップ", ["A", "B", "C", "D", "E", "F", "G", "H", "I"], index=3)
            waist = st.number_input("ウエスト", value=58)
        
        hip = st.number_input("ヒップ", value=85)

        st.divider()
        
        st.header("🎨 キャラクター設定")
        # 系統をスプレッドシートから自動取得
        types = df["系統"].unique().tolist()
        selected_type = st.selectbox("系統（お手本の選択）", types)
        
        # UIに表示するキーワード（ここをスプレッドシートの内容に合わせて調整しました）
        keywords = st.multiselect(
            "特徴キーワード（複数選択）", 
            ["清楚", "癒やし", "S感", "ギャル", "妹系", "未経験", "笑顔", "脚線美", "モデル体型", "高身長", "小柄", "色白"]
        )

    # --- メイン処理 ---
    if st.button("かりんと流でプロフを生成する"):
        if not name:
            st.warning("名前を入力してください（管理用）")
        else:
            with st.spinner("かりんと流の魔法をかけています..."):
                # 1. お手本データの抽出
                relevant_samples = df[df["系統"] == selected_type]
                if len(relevant_samples) > 0:
                    samples = relevant_samples.sample(n=min(3, len(relevant_samples)))
                    sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in samples["かりんと流プロフ全文"]])
                else:
                    sample_texts = "お手本データがありません。"

                # 2. プロンプト作成（ルールをより厳格化）
                system_prompt = "貴方はメンズエステ業界で伝説と呼ばれている、プロのライターです。上品で官能的、かつ集客力の高い文章を書くのが得意です。"
                
                user_prompt = f"""
以下の情報を元に、高級メンズエステのプロフィールを執筆してください。
提供した「お手本」のトーンを完璧に再現しつつ、以下の【禁止事項】を厳守してください。

### キャスト情報
年齢：{age}歳
サイズ：T{height} / B{bust}({cup}) / W{waist} / H{hip}
キーワード：{", ".join(keywords)}

### かりんと流・黄金ルール（絶対遵守）
1. 冒頭は【】で囲った印象的なキャッチコピーを必ず「3行」作成すること。
2. 一人称（私、僕など）は絶対に使用しない。
3. 二人称は「貴方」または「貴男」を使用すること。
4. 【禁止事項】文章の中でキャストの名前（{name}）は絶対に使わないこと。
5. 【禁止事項】キャストのことは「彼女」と呼ぶことで統一すること。
6. 【禁止事項】「昼」「夜」「深夜」など、時間帯を特定する言葉は絶対に使わない。
7. 「彼」という言葉は使わず「貴方」を使うこと。
8. 文章の最後は、期待感を最大限に煽り、今すぐ予約したくなる一文で締めること。

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
                    st.subheader(f"✨ プロフ案が完成しました")
                    st.text_area("そのままコピペして使用してください", result_text, height=600)
                    st.success("「名前なし・彼女統一」で生成されました！")
                    
                except Exception as e:
                    st.error(f"生成エラーが発生しました: {e}")

else:
    st.info("スプレッドシートのIDを正しく設定すると、ツールが表示されます。")
