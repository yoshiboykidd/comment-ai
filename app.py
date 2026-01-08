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
            with st.spinner("「彼女」という芸術を執筆中..."):
                search_word = selected_type.split('・')[0] 
                relevant_samples = df[df["系統"].str.contains(search_word, na=False)]
                
                if len(relevant_samples) > 0:
                    samples = relevant_samples.sample(n=min(3, len(relevant_samples)))
                    sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in samples["かりんと流プロフ全文"]])
                else:
                    samples = df.sample(n=3)
                    sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in samples["かりんと流プロフ全文"]])

                system_prompt = "貴方は高級メンズエステの魅力を伝える、美文の達人です。数字を情緒的に綴り、読者の想像力を掻き立てるプロフェッショナルです。"
                
                user_prompt = f"""
以下のキャスト情報を元に、気品と情熱が同居するプロフィールを執筆してください。
「お手本」の品格を保ちつつ、以下の【執筆ルール】を完璧に守ってください。

### キャスト情報
年齢：{age}歳
サイズ：身長{height}cm / B{bust}({cup}カップ) / W{waist} / H{hip}
キーワード：{", ".join(keywords)}

### かりんと流・鉄の掟（執筆ルール）
1. 冒頭に【】で囲った印象的なキャッチコピーを「3行」作成すること。
2. **【サイズ表現の極意】**: 
   「T158」「B85(D)」といった記号と数字の羅列は、機械的で色気がないため【厳禁】とする。
   数字はあくまで「彼女の魅力」を補完する要素として、文章の中に自然に、かつ官能的に溶け込ませること。
   （例：すらりと伸びた158cmの脚線美、たわわに実ったDカップの果実、きゅっと窄まった58cmの腰つき、など）
3. キャスト名（{name_admin}）は絶対に出さず、一貫して「彼女」と呼ぶこと。
4. 一人称、および時間帯（昼・夜など）を特定する言葉は使用禁止。
5. 文章の最後は、貴方の手で扉を開けたくなるような、余韻と期待を残す一文で締めること。

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
                        temperature=0.8  # 表現の柔軟性を出すために少し上げました
                    )
                    
                    result_text = response.choices[0].message.content

                    st.subheader(f"✨ 生成結果")
                    st.text_area("そのまま使用可能です", result_text, height=600)
                    st.success(f"「{selected_type}」系統の情緒的な文章が完成しました。")
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
