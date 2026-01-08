import streamlit as st
import pandas as pd
from openai import OpenAI

# ==========================================
# 設定：スプレッドシートID
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
            with st.spinner("数値を情緒的な表現に翻訳中..."):
                search_word = selected_type.split('・')[0] 
                relevant_samples = df[df["系統"].str.contains(search_word, na=False)]
                
                if len(relevant_samples) > 0:
                    samples = relevant_samples.sample(n=min(3, len(relevant_samples)))
                    sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in samples["かりんと流プロフ全文"]])
                else:
                    samples = df.sample(n=3)
                    sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in samples["かりんと流プロフ全文"]])

                system_prompt = "貴方は最高級メンズエステのプロライターです。数値を情景へと昇華させつつ、記号としての魅力を残す達人です。"
                
                user_prompt = f"""
以下のキャストデータを元に、官能的で品格のあるプロフィールを執筆してください。
「お手本」の文章構成を継承しつつ、以下の【鉄の掟】を完璧に守ってください。

### 素材となるデータ
年齢：{age}歳
身長：{height}cm / バスト：{bust}({cup}カップ) / ウエスト：{waist} / ヒップ：{hip}
キーワード：{", ".join(keywords)}

### かりんと流・鉄の掟（絶対遵守）
1. **【数値の扱い（重要）】**: 
   - 「158cm」「58cm」「85cm」などの具体的な**cm単位の数値は本文に出すことを一切禁止**とする。
   - 代わりに、その数値が意味する「魅力」を詩的・情緒的な言葉で表現すること（例：掌に収まりそうな可憐な体躯、繊細に窄まった腰つき、等）。
   - ただし、**カップ数（{cup}カップ、または{cup}）というアルファベット表記のみ、具体的に本文中で使用して良い**。
2. 冒頭に【】で囲ったキャッチコピーを「3行」作成すること。
3. キャスト名（{name_admin}）は絶対に出さず、一貫して「彼女」と呼ぶこと。
4. 一人称、および時間帯（昼・夜など）を特定する言葉は使用禁止。
5. 最後は、彼女との時間を心待ちにさせるような、余韻のある一文で締めること。

作成された文章：
"""

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.8
                    )
                    
                    result_text = response.choices[0].message.content

                    st.subheader(f"✨ 生成結果")
                    st.text_area("そのまま使用可能です", result_text, height=600)
                    st.success(f"「{cup}カップ」の魅力を際立たせた文章が完成しました。")
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
