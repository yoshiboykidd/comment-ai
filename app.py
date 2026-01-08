import streamlit as st
import pandas as pd
from openai import OpenAI

# ==========================================
# 1. 設定：ここにご自身のスプレッドシートIDを入れてください
# ==========================================
# スプレッドシートのURL（/d/ と /edit の間の長い英数字）をここに貼り付け
SPREADSHEET_ID = "1sIr-8ys0jSapzIlt8RSei4lYIKPbFdZjm5OofizxmYM"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"

# OpenAIクライアントの初期化（StreamlitのSecretsから読み込み）
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 画面設定 ---
st.set_page_config(page_title="かりんと流・プロフ生成ツール", page_icon="✨", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #fff5f7; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff4b6e; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ かりんと流・プロフ生成ツール")
st.caption("スプレッドシートの最新学習データから「売れるプロフ」を自動生成します")

# --- データの読み込み（自動更新：10分キャッシュ） ---
@st.cache_data(ttl=600)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        # 必要な列があるかチェック
        required_cols = ["系統", "かりんと流プロフ全文"]
        if not all(col in data.columns for col in required_cols):
            st.error("スプレッドシートの列名が正しくありません。「系統」「かりんと流プロフ全文」という列が必要です。")
            return None
        return data
    except Exception as e:
        st.error(f"データの読み込みに失敗しました。スプレッドシートの共有設定が「リンクを知っている全員」になっているか確認してください。")
        return None

df = load_data()

if df is not None:
    # --- サイドバー：入力フォーム ---
    with st.sidebar:
        st.header("👤 キャスト基本情報")
        name = st.text_input("名前", placeholder="例：あやか")
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
        
        keywords = st.multiselect(
            "特徴キーワード（複数選択）", 
            ["清楚", "癒やし", "S感", "ギャル", "妹系", "未経験", "笑顔", "脚線美", "色白", "巨乳", "スレンダー"]
        )

    # --- メイン処理 ---
    if st.button("かりんと流でプロフを生成する"):
        if not name:
            st.warning("キャストの名前を入力してください。")
        else:
            with st.spinner("スプレッドシートから最適なサンプルを探して執筆中..."):
                # 1. お手本データの抽出（選択された系統から最大3件を抽出）
                relevant_samples = df[df["系統"] == selected_type]
                if len(relevant_samples) > 0:
                    samples = relevant_samples.sample(n=min(3, len(relevant_samples)))
                    sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in samples["かりんと流プロフ全文"]])
                else:
                    sample_texts = "お手本データがありません。"

                # 2. プロンプト作成（かりんと流・黄金ルール）
                system_prompt = "貴方はメンズエステ業界で伝説と呼ばれている、プロのライターです。上品で官能的、かつ集客力の高い文章を書くのが得意です。"
                
                user_prompt = f"""
以下のキャスト情報を元に、高級メンズエステのプロフィールを作成してください。
提供した「参考にする文章スタイル（お手本）」のトーンや言葉遣いを完璧にコピーしつつ、新しい内容を執筆してください。

### キャスト情報
名前：{name}
年齢：{age}歳
サイズ：T{height} / B{bust}({cup}) / W{waist} / H{hip}
キーワード：{", ".join(keywords)}

### かりんと流・黄金ルール
1. 冒頭は【】で囲った印象的なキャッチコピーを3行作成すること。
2. 一人称（私、僕など）は絶対に使用しない。
3. 二人称は「貴方」または「貴男」を使用すること。
4. キャストのことは「彼女」または「{name}」と呼ぶこと。
5. 時間帯（昼、夜、深夜）を特定する言葉は使わないこと（24時間運用のため）。
6. 「彼」という言葉は使わず「貴方」を使うこと。
7. 文章の最後は、期待感を最大限に煽り、指名したくなる一文で締めること。

### 参考にする文章スタイル（お手本）
{sample_texts}

作成された文章：
"""

                try:
                    # 3. OpenAI API呼び出し
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
                    st.subheader(f"✨ {name} さんのプロフ案")
                    st.text_area("コピーして使用してください", result_text, height=600)
                    st.success("生成が完了しました！")
                    
                except Exception as e:
                    st.error(f"生成エラーが発生しました: {e}")

else:
    st.info("スプレッドシートのIDを正しく設定すると、ここにツールが表示されます。")
