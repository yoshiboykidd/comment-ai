import streamlit as st
import pandas as pd
from openai import OpenAI

# ==========================================
# 1. セキュリティ設定：Secretsから読み込み
# ==========================================
# GitHubを公開にしても、IDとKeyはStreamlitの金庫（Secrets）にあるので安全です
try:
    SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("StreamlitのSecrets設定が見つかりません。管理画面でIDとAPIキーを登録してください。")
    st.stop()

SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"
TARGET_PASSWORD = "karin10"

client = OpenAI(api_key=OPENAI_API_KEY)

# --- 画面設定 ---
st.set_page_config(page_title="かりんと流・プロフ生成ツール", page_icon="✨", layout="centered")

# デザイン調整
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
# 2. メインツール部分（認証成功時のみ表示）
# ==========================================
if check_password():

    st.title("✨ かりんと流・プロフ生成ツール")
    st.caption("情緒的な表現と二面性のギャップで、指名したくなるプロフを綴ります。")

    @st.cache_data(ttl=600)
    def load_data():
        try:
            data = pd.read_csv(SHEET_URL)
            return data
        except Exception as e:
            st.error("スプレッドシートの読み込みに失敗しました。共有設定を確認してください。")
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

        # --- 生成実行 ---
        if st.button("かりんと流でプロフを生成する"):
            if not name_admin:
                st.warning("キャストの名前を入力してください")
            else:
                with st.spinner("「彼女」だけの特別な物語を執筆中..."):
                    # 1. お手本の抽出
                    search_word = selected_type.split('・')[0] 
                    relevant_samples = df[df["系統"].str.contains(search_word, na=False)]
                    
                    if len(relevant_samples) > 0:
                        samples = relevant_samples.sample(n=min(3, len(relevant_samples)))
                        sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in samples["かりんと流プロフ全文"]])
                    else:
                        samples = df.sample(n=3)
                        sample_texts = "\n\n".join([f"--- お手本 ---\n{text}" for text in samples["かりんと流プロフ全文"]])

                    # 2. プロンプト（鉄の掟）
                    system_prompt = "貴方は最高級メンズエステのプロライターです。数値を情景へと昇華させ、読者を虜にする達人です。"
                    
                    user_prompt = f"""
以下のキャストデータを元に、官能的で品格のあるプロフィールを執筆してください。
「お手本」の文章構成を継承しつつ、以下の【鉄の掟】を完璧に守ってください。

### キャストデータ
年齢：{age}歳 / 身長：{height}cm / バスト：{bust}({cup}カップ) / ウエスト：{waist} / ヒップ：{hip}
キーワード：{", ".join(keywords)}

### かりんと流・鉄の掟（絶対遵守）
1. **【数値の完全排除とカップ数表記】**: 
   - 身長・ウエスト・ヒップなどの具体的なcm数値は本文に【一切出さない】こと。代わりに、その数値が意味する「魅力（小柄、すらりとした、繊細なくびれ等）」を詩的な言葉で表現すること。
   - ただし、**カップ数（{cup}カップ、または{cup}）という記号のみ**は、具体的に本文中で使用して良い。
2. **【ギャップの魔法】**: 
   - 選択されたキーワードに矛盾（例：清楚とS感、妹系と大人など）がある場合、それを「二面性」として昇華させ、魅力的なストーリーとして織り交ぜること。
3. **【呼称と禁止ワード】**:
   - キャスト名（{name_admin}）は絶対に出さず、一貫して「彼女」と呼ぶこと。
   - 一人称（私など）、および時間帯（昼・夜など）を特定する言葉は使用禁止。
4. 冒頭に【】で囲った印象的なキャッチコピーを必ず「3行」作成すること。
5. 最後は、期待感を最高潮に高め、予約へと誘う最高の一文で締めること。

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
                            temperature=0.8
                        )
                        
                        result_text = response.choices[0].message.content
                        st.subheader(f"✨ {name_admin} さんの生成結果")
                        st.text_area("そのまま使用可能です", result_text, height=600)
                        st.success("「彼女」で統一された情緒的なプロフが完成しました。")
                        
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
