import streamlit as st
import pandas as pd
from openai import OpenAI

# ==========================================
# 1. 設定：スプレッドシートIDと合言葉
# ==========================================
SPREADSHEET_ID = "1sIr-8ys0jSapzIlt8RSei4lYIKPbFdZjm5OofizxmYM"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"
TARGET_PASSWORD = "karin10"  # ←合言葉をこちらに設定しました

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 画面設定 ---
st.set_page_config(page_title="かりんと流・プロフ生成ツール", page_icon="✨", layout="centered")

# デザイン
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

# --- 簡易認証機能 ---
def check_password():
    """合言葉が正しいかチェックする関数"""
    if "password_correct" not in st.session_state:
        # 初回表示
        st.title("🔒 Security Check")
        st.text_input("合言葉を入力してください", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # 間違えた場合
        st.title("🔒 Security Check")
        st.text_input("合言葉を入力してください", type="password", on_change=password_entered, key="password")
        st.error("😕 合言葉が違います")
        return False
    else:
        # 正解
        return True

def password_entered():
    """入力された合言葉を判定する関数"""
    if st.session_state["password"] == TARGET_PASSWORD:
        st.session_state["password_correct"] = True
        del st.session_state["password"]  # セキュリティのため入力値を削除
    else:
        st.session_state["password_correct"] = False

# ==========================================
# 2. メインツール部分（認証成功時のみ表示）
# ==========================================
if check_password():

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
            st.header("👤 キャスト基本情報")
            name_admin = st.text_input("キャスト名（管理用）", placeholder="例：あやか")
            age = st.number_input("年齢", min_value=18, max_value=60, value=20)
            
            st.subheader("📏 サイズ（数値はイメージ変換用）")
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
            display_types = ["清楚・癒やし", "モデル・上品", "妹・アイドル", "ギャル・小悪魔", "大人・お姉さん"]
            selected_type = st.selectbox("基本系統（お手本の選択）", display_types)
            
            keywords = st.multiselect(
                "特徴キーワード", 
                ["清楚", "癒やし", "S感", "ギャル", "妹系", "未経験", "笑顔", "脚線美", "モデル体型", 
                 "高身長", "小柄", "色白", "豊満", "スレンダー", "人妻風", "JD", "ハーフ顔", "愛嬌", 
                 "しっとり", "聞き上手", "美乳", "美肌", "モチモチ肌", "おっとり", "活発"]
            )

            st.divider()
            if st.button("ログアウト"):
                st.session_state["password_correct"] = False
                st.rerun()

        if st.button("かりんと流でプロフを生成する"):
            if not name_admin:
                st.warning("キャストの名前を入力してください")
            else:
                with st.spinner("二面性の魅力を執筆中..."):
                    search_word = selected_type.split('・')[0] 
                    relevant_samples = df[df["系統"].str.contains(search_word, na=False)]
                    
                    if len(relevant_samples) > 0:
                        samples = relevant_samples.sample(n=min(3, len(relevant_samples)))
                        sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in samples["かりんと流プロフ全文"]])
                    else:
                        samples = df.sample(n=3)
                        sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in samples["かりんと流プロフ全文"]])

                    system_prompt = "貴方は最高級メンズエステのプロライターです。キャストの二面性を『ギャップ』に変えて、読者を虜にする文章を書きます。"
                    
                    user_prompt = f"""
以下のキャストデータを元に、高級感と期待感に満ちたプロフィールを執筆してください。
「お手本」の品格を保ちつつ、以下の【鉄の掟】を完璧に守ってください。

### キャストデータ
年齢：{age}歳
身長：{height}cm / バスト：{bust}({cup}カップ) / ウエスト：{waist} / ヒップ：{hip}
キーワード：{", ".join(keywords)}

### かりんと流・鉄の掟（絶対遵守）
1. **【ギャップの魔法】**: 相反するキーワードがある場合、それを「最高の二面性」として昇華させること。
2. **【数値の完全排除とカップ数表記】**: 
   - 身長・ウエスト・ヒップなどの具体的なcm数値は本文に【一切出さない】こと。その数値が意味する「魅力」を詩的な言葉で表現すること。
   - ただし、**カップ数（{cup}カップ、または{cup}）という記号のみ**は、具体的に本文中で使用して良い。
3. 冒頭に【】で囲った印象的なキャッチコピーを必ず「3行」作成すること。
4. キャスト名（{name_admin}）は絶対に出さず、一貫して「彼女」と呼ぶこと。一人称、および時間帯表現は使用禁止。
5. 最後は、彼女の「真実の姿」を予感させるような、期待に満ちた一文で締めること。

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
                        
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
