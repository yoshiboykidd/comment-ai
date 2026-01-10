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
    st.error("Secrets設定が見つかりません。")
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
    .stCheckbox label { font-size: 14px; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# --- 簡易認証機能 ---
if "password_correct" not in st.session_state:
    st.title("🔒 Security Check")
    pw = st.text_input("合言葉を入力してください", type="password")
    if st.button("ログイン"):
        if pw == TARGET_PASSWORD:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("😕 合言葉が違います")
    st.stop()

# ==========================================
# 2. メインツール部分
# ==========================================
st.title("✨ かりんと流・プロフ生成ツール")

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
        # --- 1. キャスト基本情報 ---
        st.header("👤 キャスト基本情報")
        name_admin = st.text_input("キャスト名", placeholder="あやか")
        age = st.number_input("年齢", min_value=18, max_value=60, value=20)
        
        st.divider()

        # --- 2. サイズ情報 ---
        st.header("📏 サイズ")
        c1, c2 = st.columns(2)
        with c1:
            height = st.number_input("身長(cm)", value=158)
            bust = st.number_input("バスト(cm)", value=85)
        with c2:
            cup = st.selectbox("カップ", ["A", "B", "C", "D", "E", "F", "G", "H", "I"], index=3)
            waist = st.number_input("ウエスト(cm)", value=58)
        hip = st.number_input("ヒップ(cm)", value=85)

        st.divider()

        # --- 3. 執筆方針（ベーススタイル） ---
        st.header("💎 執筆方針の決定")
        selected_style = st.selectbox(
            "全体の雰囲気（ベーススタイル）", 
            ["清楚・可憐", "妖艶・色香", "親近感・ナチュラル", "都会的・洗練", "天真爛漫・愛嬌", "慈愛・包容力", "知的・ミステリアス", "和風・しとやか"]
        )

        st.divider()

        # --- 4. 特徴キーワードの選定 ---
        st.header("🎨 特徴キーワードの選定")
        all_selected_keywords = []
        def create_checkbox_grid(title, options, cols_num=2):
            st.subheader(title)
            selected = []
            cols = st.columns(cols_num)
            for i, option in enumerate(options):
                if cols[i % cols_num].checkbox(option, key=f"key_{option}"):
                    selected.append(option)
            return selected

        all_selected_keywords += create_checkbox_grid("・系統・味付け", ["清楚", "癒やし", "ギャル", "妹系", "JD", "人妻風", "ハーフ顔", "都会的", "未経験"])
        all_selected_keywords += create_checkbox_grid("・外見特徴", ["美脚", "モデル体型", "高身長", "小柄", "色白", "巨乳", "スレンダー", "美乳", "美肌", "モチモチ肌"])
        all_selected_keywords += create_checkbox_grid("・性格・接客", ["笑顔", "愛嬌", "しっとり", "聞き上手", "おっとり", "活発", "一生懸命", "クール"])
        # 【更新】「責め好き」を追加
        all_selected_keywords += create_checkbox_grid("・ギャップ", ["S感", "清楚なのに大胆", "ギャルなのに健気", "実は情熱的", "ギャップ萌え", "エッチ好き", "責め好き"])

        st.divider()
        st.header("📝 文章のボリューム")
        length_preset = st.radio("文字数目安", ["標準（400文字）", "短め（200文字）", "長め（800文字）", "数値指定"], index=0)
        target_len = f"約{st.number_input('希望文字数', 50, 2000, 300) if length_preset == '数値指定' else length_preset}"

        st.divider()
        if st.button("ログアウト"):
            st.session_state["password_correct"] = False
            st.rerun()

    # --- 生成実行 ---
    if st.button("かりんと流でプロフを生成する"):
        if not name_admin:
            st.warning("キャスト名を入力してください")
        elif not all_selected_keywords:
            st.warning("キーワードを選択してください")
        else:
            with st.spinner("キャッチコピーと物語を執筆中..."):
                search_word = selected_style.split('・')[0] if '・' in selected_style else selected_style
                relevant_samples = df[df["系統"].str.contains(search_word, na=False)]
                sample_texts = "\n\n".join([f"--- 参考 ---\n{text}" for text in relevant_samples.sample(n=min(3, len(relevant_samples)))["かりんと流プロフ全文"]]) if len(relevant_samples) > 0 else ""

                system_prompt = "あなたは高級メンズエステのプロライターです。構成を遵守し、読者の想像力を最高潮に高める詩的で官能的な文章を綴ります。"
                
                user_prompt = f"""
以下のデータを元に、新マスタールールを厳守してプロフィールを執筆してください。

### 素材データ
名前：{name_admin} / ベーススタイル：{selected_style}
キーワード：{", ".join(all_selected_keywords)}
身体：{cup}カップ / 指定文字数：{target_len}

### 【構成の掟：絶対に省略禁止】
1. **冒頭に必ず【】で囲ったキャッチコピーを「3行」作成すること。**
2. 次に本文を開始し、「第一印象」→「ギャップ」→「身体描写」→「余韻」の順で構成すること。

### 【かりんと流・鉄の掟】
- 主語は「彼女」、お客様は「貴方」で固定。
- 数値（cm）は出さず、詩的な表現に変換（例：掌に余る{cup}カップの果実）。
- 具体的な時間は排除し「ふたりきりの刻」等に置換。
- 「責め好き」という要素は、品格を保ちつつ「攻めの奉仕による官能的なギャップ」として昇華させること。

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
