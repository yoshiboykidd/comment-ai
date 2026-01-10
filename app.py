import streamlit as st
import pandas as pd
from openai import OpenAI

# ==========================================
# 1. セキュリティ設定
# ==========================================
try:
    SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("Secrets設定が見つかりません。管理画面で設定してください。")
    st.stop()

SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"
TARGET_PASSWORD = "karin10"

client = OpenAI(api_key=OPENAI_API_KEY)

# --- 画面設定 ---
st.set_page_config(page_title="かりんと流・プロフ生成ツール", page_icon="✨", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #fffafb; }
    .stButton>button { 
        width: 100%; border-radius: 20px; background-color: #ff4b6e; 
        color: white; font-weight: bold; height: 3.5em; border: none;
    }
    .stButton>button:hover { background-color: #ff2a51; }
    </style>
    """, unsafe_allow_html=True)

# --- 簡易認証機能 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔒 Security Check")
        st.text_input("合言葉を入力してください", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔒 Security Check")
        st.text_input("合言葉を入力してください", type="password", on_change=password_entered, key="password")
        st.error("😕 合言葉が違います")
        return False
    else:
        return True

def password_entered():
    if st.session_state["password"] == TARGET_PASSWORD:
        st.session_state["password_correct"] = True
        del st.session_state["password"]
    else:
        st.session_state["password_correct"] = False

# ==========================================
# 2. メインツール部分
# ==========================================
if check_password():
    st.title("✨ かりんと流・プロフ生成ツール")
    st.caption("新マスタールール準拠：文字数の数値指定に対応")

    @st.cache_data(ttl=600)
    def load_data():
        try:
            data = pd.read_csv(SHEET_URL)
            return data
        except Exception as e:
            st.error("データの読み込みに失敗しました。")
            return None

    df = load_data()

    if df is not None:
        with st.sidebar:
            st.header("👤 基本情報")
            name_admin = st.text_input("キャスト名", placeholder="あやか")
            age = st.number_input("年齢", min_value=18, max_value=60, value=20)
            
            st.subheader("📏 サイズ")
            c1, c2 = st.columns(2)
            with c1:
                height = st.number_input("身長(cm)", value=158)
                bust = st.number_input("バスト(cm)", value=85)
            with c2:
                cup = st.selectbox("カップ", ["A", "B", "C", "D", "E", "F", "G", "H", "I"], index=3)
                waist = st.number_input("ウエスト(cm)", value=58)
            hip = st.number_input("ヒップ(cm)", value=85)

            st.divider()
            st.header("🎨 キャラクター設定")
            
            v_keys = st.multiselect("① 系統・雰囲気", ["清楚", "癒やし", "ギャル", "妹系", "JD", "人妻風", "ハーフ顔", "クール", "都会的", "未経験"])
            b_keys = st.multiselect("② 外見特徴", ["美脚", "モデル体型", "高身長", "小柄", "色白", "巨乳", "スレンダー", "美乳", "美肌", "モチモチ肌"])
            s_keys = st.multiselect("③ 性格・接客", ["笑顔", "愛嬌", "しっとり", "聞き上手", "おっとり", "活発", "一生懸命"])
            g_keys = st.multiselect("④ ギャップ", ["S感", "清楚なのに大胆", "ギャルなのに健気", "実は情熱的", "ギャップ萌え"])

            all_keywords = v_keys + b_keys + s_keys + g_keys
            selected_type = st.selectbox("お手本にする系統", ["清楚・癒やし", "モデル・上品", "妹・アイドル", "ギャル・小悪魔", "大人・お姉さん"])

            st.divider()
            # --- 【修正】文字数指定セクション（数値入力） ---
            st.header("📝 文字数の設定")
            length_preset = st.radio(
                "文字数目安を選択",
                ["標準（400文字）", "短め（200文字）", "長め（800文字）", "数値を指定する"],
                index=0
            )
            
            target_length_str = ""
            if length_preset == "数値を指定する":
                custom_num = st.number_input("希望の文字数を入力", min_value=50, max_value=2000, value=300, step=50)
                target_length_str = f"全体で約{custom_num}文字程度"
            else:
                target_length_str = f"全体で約{length_preset.replace('程度', '')}前後"
            
            st.divider()
            if st.button("ログアウト"):
                st.session_state["password_correct"] = False
                st.rerun()

        # --- 生成実行 ---
        if st.button("かりんと流でプロフを生成する"):
            if not name_admin:
                st.warning("キャスト名を入力してください")
            elif not all_keywords:
                st.warning("キーワードを1つ以上選択してください")
            else:
                with st.spinner("指定された文字数で執筆中..."):
                    # お手本抽出
                    search_word = selected_type.split('・')[0] 
                    relevant_samples = df[df["系統"].str.contains(search_word, na=False)]
                    sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in relevant_samples.sample(n=min(3, len(relevant_samples)))["かりんと流プロフ全文"]]) if len(relevant_samples) > 0 else ""

                    system_prompt = "あなたは高級手コキオナクラ専門のライターです。数値を情景へと昇華させ、詩的な文章を綴ります。"
                    
                    user_prompt = f"""
以下のデータを元に、新マスタールールを厳守してプロフィールを執筆してください。

### 素材データ
名前：{name_admin} / 身長：{height}cm / バスト：{bust}({cup}カップ) / ウエスト：{waist} / ヒップ：{hip}
キーワード：{", ".join(all_keywords)}

### 【重要】文章の長さ
指示：{target_length_str}（この文字数に近づけて執筆してください）

### かりんと流・新マスタールール（絶対遵守）
1. **【人称の掟】**: 本文は「彼女」と「貴方」のみ。
2. **【世界観・時間の掟】**: 「朝昼夜」の時間は排除。
3. **【トーンと表現の掟】**: 比喩を用いた詩的官能。
4. **【構成の掟】**: ①冒頭【】3行、②第一印象、③ギャップ、④体の特徴（cm数値は出さず{cup}カップ等の記号と表現）、⑤余韻
5. **【禁止事項】**: 同一フレーズの繰り返し禁止。

作成された文章：
"""
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                            temperature=0.8
                        )
                        st.subheader(f"✨ {name_admin} さんの生成結果")
                        st.text_area("そのままコピー可能です", response.choices[0].message.content, height=650)
                    except Exception as e:
                        st.error(f"エラー: {e}")
