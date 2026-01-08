import streamlit as st
import pandas as pd
from openai import OpenAI

# ==========================================
# 設定：スプレッドシートID（適用済み）
# ==========================================
SPREADSHEET_ID = "1sIr-8ys0jSapzIlt8RSei4lYIKPbFdZjm5OofizxmYM"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 画面設定 ---
st.set_page_config(page_title="かりんと流・プロフ生成ツール", page_icon="✨", layout="centered")

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
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ かりんと流・プロフ生成ツール")

@st.cache_data(ttl=600)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        return data
    except Exception as e:
        st.error("スプレッドシートの読み込みに失敗しました。")
        return None

df = load_data()

if df is not None:
    with st.sidebar:
        st.header("👤 キャスト基本情報")
        name_admin = st.text_input("キャスト名（管理用）", placeholder="例：あやか")
        age = st.number_input("年齢", min_value=18, max_value=60, value=20)
        
        st.subheader("📏 サイズ（数値はイメージ変換用）")
        c1, c2 = st.columns(2)
        with c1:
            height = st.number_input("身長(cm)", value=158)
            bust = st.number_input("バスト", value=85)
        with c2:
            cup = st.selectbox("カップ", ["A", "B", "C", "D", "E", "F", "G", "H", "I"], index=3)
            waist = st.number_input("ウエスト(cm)", value=58)
        hip = st.number_input("ヒップ(cm)", value=85)

        st.divider()
        
        st.header("🎨 キャラクター設定")
        display_types = ["清楚・癒やし", "モデル・上品", "妹・アイドル", "ギャル・小悪魔", "大人・お姉さん"]
        selected_type = st.selectbox("基本系統（お手本の選択）", display_types)
        
        keywords = st.multiselect(
            "特徴キーワード", 
            ["清楚", "癒やし", "S感", "ギャル", "妹系", "未経験", "笑顔", "脚線美", "モデル体型", 
             "高身長", "小柄", "色白", "豊満", "スレンダー", "人妻風", "JD", "ハーフ顔", "愛嬌", 
             "しっとり", "聞き上手", "美乳", "美肌", "モチモチ肌", "おっとり", "活発"]
        )

    if st.button("かりんと流でプロフを生成する"):
        if not name_admin:
            st.warning("キャストの名前を入力してください")
        else:
            with st.spinner("二面性の魅力を執筆中..."):
                search_word =
