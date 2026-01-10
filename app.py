import streamlit as st
import pandas as pd
from openai import OpenAI

# ==========================================
# 1. セキュリティ・基盤設定
# ==========================================
try:
    SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("Secrets設定（SPREADSHEET_ID, OPENAI_API_KEY）が未設定です。")
    st.stop()

SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"
TARGET_PASSWORD = "karin10"
client = OpenAI(api_key=OPENAI_API_KEY)

# --- 画面設定 ---
st.set_page_config(page_title="かりんと流・プロフ生成ツール", page_icon="✨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fffafb; }
    .stButton>button { 
        width: 100%; border-radius: 12px; background-color: #ff4b6e; 
        color: white; font-weight: bold; height: 3.5em; border: none;
    }
    .stCheckbox label { font-size: 15px; font-weight: 500; }
    .report-area { background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #ffcce0; line-height: 1.8; }
    </style>
    """, unsafe_allow_html=True)

# --- 認証機能 ---
if "password_correct" not in st.session_state:
    st.title("🔒 Security Check")
    pw = st.text_input("合言葉を入力してください", type="password")
    if st.button("ログイン"):
        if pw == TARGET_PASSWORD:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("合言葉が違います")
    st.stop()

# ==========================================
# 2. データ読み込み & UI構築
# ==========================================
st.title("✨ かりんと流・プロフ生成ツール")
st.caption("新マスタールール準拠：プロライター執筆×最新キーワード精査モデル")

@st.cache_data(ttl=600)
def load_data():
    try:
        return pd.read_csv(SHEET_URL)
    except:
        return None

df = load_data()

with st.sidebar:
    st.header("👤 キャスト基本情報")
    name_admin = st.text_input("名前", placeholder="あみ")
    age = st.number_input("年齢", 18, 35, 20)
    
    st.divider()
    st.header("📏 サイズ")
    c1, c2 = st.columns(2)
    with c1:
        height = st.number_input("身長(cm)", value=158)
        bust = st.number_input("バスト(cm)", value=85)
    with c2:
        cup = st.selectbox("カップ", ["A","B","C","D","E","F","G","H","I以上"], index=3)
        waist = st.number_input("ウエスト(cm)", value=58)
    hip = st.number_input("ヒップ(cm)", value=85)

    st.divider()
    selected_style = st.selectbox(
        "全体の雰囲気（ベーススタイル）", 
        ["清楚・可憐", "妖艶・色香", "親近感・ナチュラル", "都会的・洗練", "天真爛漫・愛嬌", "女子アナ風・気品", "地雷・量産型トレンド"]
    )
    
    st.divider()
    target_length = st.slider("目標文字数（デフォルト400字）", 200, 800, 400, step=50)

# --- キーワード選定（全表示チェックボックス形式） ---
st.header("🎨 特徴キーワードの選定")

def create_checkbox_grid(title, options, cols_num=4):
    st.subheader(title)
    selected = []
    cols = st.columns(cols_num)
    for i, option in enumerate(options):
        if cols[i % cols_num].checkbox(option, key=f"opt_{option}"):
            selected.append(option)
    return selected

kw_visual = create_checkbox_grid("① 系統・ビジュアル", ["美人", "可愛い", "清楚", "正統派", "透明感", "癒し系", "アイドル系", "小動物系", "ギャル", "派手", "地雷・量産型", "韓国風", "ハーフ顔", "ボーイッシュ", "綺麗なお姉さん", "女子アナ系", "モデル系"])
kw_status = create_checkbox_grid("② 属性・ステータス", ["現役感", "フレッシュ", "女子大生", "OL", "専門学生"])
kw_personality = create_checkbox_grid("③ 接客・味付け", ["天真爛漫", "ノリが良い", "神対応", "聞き上手", "おっとり", "真面目・一生懸命", "甘えん坊", "人懐っこい", "小悪魔", "ツンデレ"])
kw_gap = create_checkbox_grid("④ 秘密のギャップ（戦略要素）", ["実はグラマラス", "マシュマロ肌・ボディ", "実は積極的", "清楚なのに大胆", "ギャルなのに健気"])

all_keywords = kw_visual + kw_status + kw_personality + kw_gap

# ==========================================
# 3. 生成実行（新マスタールール厳守プロンプト）
# ==========================================
if st.button("かりんと流でプロフを生成する"):
    if not name_admin or not all_keywords:
        st.warning("名前とキーワードを入力してください")
    else:
        with st.spinner("「かりんと流マスタールール」に基づき執筆中..."):
            
            system_msg = "あなたは高級オナクラ専門の伝説的ライターです。数値を情景へと昇華させ、読者の想像力を掻き立てる詩的な文章を綴ります。"
            
            user_msg = f"""
以下のデータを元に、新マスタールールを厳守してプロフィールを執筆してください。

### 素材データ
名前：{name_admin} / 年齢：{age}歳 / 身長：{height}cm / B{bust}({cup}カップ) W{waist} H{hip}
選択された要素：{", ".join(all_keywords)}
ベーススタイル：{selected_style}

### かりんと流・新マスタールール（絶対遵守）
1. **【冒頭の掟】**: 一番最初に、その子を表すアイキャッチ的な3行のキャッチコピーを【】で囲んで出力してください。
2. **【人称の掟】**: 本文は「彼女」と「貴方」のみ。名前や一人称(私等)の使用は厳禁。
3. **【時間の掟】**: 「朝昼夜」などの日常的な時間は排除し、「ふたりきりの刻」等に置換。
4. **【描写の掟】**: 数値をそのまま出さず、{cup}カップの質感や柔らかさ、温度感といった情景へ昇華させること。
5. **【ギャップ戦略】**: 「{selected_style}」という器の中に、選択されたキーワード（特にギャップ要素）を「貴方だけに見せる特別な二面性」としてストーリー化。
6. **【構成】**: ①【3行キャッチ】、②第一印象、③ギャップ、④肉体の詩、⑤余韻
7. **【文字数】**: 約{target_length}文字程度

作成された文章：
"""
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg}
                    ],
                    temperature=0.8
                )
                
                result_text = response.choices[0].message.content
                st.subheader(f"✨ {name_admin} さんの生成結果")
                st.text_area("そのままコピー可能です", result_text, height=600)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
