import streamlit as st
import pandas as pd
import openai

# --- 1. 定数・キーワード設定（36項目） ---
STYLES = ["清楚・可憐", "妖艶・色香", "親近感・ナチュラル", "都会的・洗練", "天真爛漫・愛嬌", "女子アナ風・気品", "地雷・量産型トレンド"]

TYPES = ["清楚", "癒し系", "綺麗系", "可愛い系", "ロリ系", "ギャル系", "モデル系", "お姉さん系"]
LOOKS = ["スレンダー", "セクシー", "グラマー", "巨乳", "微乳", "美肌", "色白", "美乳", "美脚", "美尻"]
PERSONALITY = ["明るい", "甘えん坊", "ツンデレ", "恥ずかしがり屋", "人懐っこい", "愛嬌抜群", "しっかり者", "聞き上手", "天然", "オタク", "おっとり"]
FEATURES = ["黒髪", "完全未経験", "処女", "スタイル抜群", "テクニシャン", "責め好き", "エッチ好き"]

# --- 2. 認証機能 ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔐 かりんと流 ログイン")
        password = st.text_input("パスワードを入力してください", type="password")
        if st.button("ログイン"):
            if password == "karin10":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("パスワードが違います。")
        return False
    return True

# --- 3. データベース読み込み機能 ---
@st.cache_data
def load_database():
    try:
        df = pd.read_csv("database.csv", sep=None, engine='python', encoding='utf-8-sig')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"データベースの読み込みに失敗しました。")
        return None

# --- 4. お手本検索ロジック ---
def find_best_samples(df, selected_style, selected_keywords):
    if df is None or df.empty:
        return "※お手本なしで執筆します。"
    
    col_name = "全体の雰囲気" if "全体の雰囲気" in df.columns else df.columns[0]
    filtered_df = df[df[col_name] == selected_style]
    
    if filtered_df.empty:
        filtered_df = df
    
    def score_row(row):
        kw_col = "特徴キーワード" if "特徴キーワード" in df.columns else df.columns[1]
        db_kws = str(row[kw_col]).replace(" ", "").split(",")
        return len(set(selected_keywords) & set(db_kws))
    
    filtered_df["score"] = filtered_df.apply(score_row, axis=1)
    best_samples = filtered_df.sort_values(by="score", ascending=False).head(2)
    
    sample_text = ""
    content_col = "該当キャストのプロフ本文" if "該当キャストのプロフ本文" in df.columns else df.columns[-1]
    for _, row in best_samples.iterrows():
        sample_text += f"\n---\n【過去の傑作お手本】\n{row[content_col]}\n"
    
    return sample_text

# --- メイン画面 ---
if check_password():
    st.set_page_config(page_title="かりんと流・プロフ生成 ver 2.0", layout="centered")
    st.title("✨ かりんと流・プロフ生成ツール ver 2.0")

    if "result_text" not in st.session_state:
        st.session_state.result_text = ""

    st.divider()
    st.header("1. キャスト基本情報")
    col_name, col_style = st.columns(2)
    with col_name:
        cast_name = st.text_input("キャスト名（管理用）", placeholder="例：あやか")
    with col_style:
        base_style = st.selectbox("ベースとなる系統", STYLES)

    st.subheader("スペック詳細")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: age = st.number_input("年齢", min_value=18, max_value=60, value=22)
    with c2: height = st.number_input("身長", min_value=130, max_value=200, value=158)
    with c3: bust = st.number_input("バスト", min_value=70, max_value=130, value=85)
    with c4: cup = st.selectbox("カップ", ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"], index=3)
    with c5: waist = st.number_input("ウエスト", min_value=40, max_value=120, value=58)
    with c6: hip = st.number_input("ヒップ", min_value=70, max_value=130, value=86)

    full_spec = f"（{age}）T:{height} B:{bust}({cup}) W:{waist} H:{hip}"
    st.info(f"参照用スペック： {full_spec}")

    st.divider()
    st.header("2. 特徴タグの選択")
    all_selected_keywords = []

    def create_checkbox_grid(label, options, key_prefix):
        st.subheader(label)
        cols = st.columns(4)
        selected = []
        for i, option in enumerate(options):
            if cols[i % 4].checkbox(option, key=f"{key_prefix}_{option}"):
                selected.append(option)
        return selected

    all_selected_keywords += create_checkbox_grid("●タイプ", TYPES, "type")
    all_selected_keywords += create_checkbox_grid("●ルックス", LOOKS, "look")
    all_selected_keywords += create_checkbox_grid("●性格", PERSONALITY, "pers")
    all_selected_keywords += create_checkbox_grid("●特徴・個性", FEATURES, "feat")

    st.divider()

    if st.button("✨ かりんと流で執筆を開始する", type="primary", use_container_width=True):
        if not cast_name or not all_selected_keywords:
            st.error("入力が不足しています。")
        else:
            db = load_database()
            samples = find_best_samples(db, base_style, all_selected_keywords)
            
            # --- かりんと流・執筆プロンプト（最新ルール適用） ---
            system_prompt = f"""
あなたは日本人女性専門のカリスマライター「かりんと」です。
提供されたデータベースにある「過去の傑作」の文体・リズム・美意識を完璧に継承し、新しいキャストのプロフィールを執筆してください。

【絶対ルール：かりんと流・執筆憲法】
1. ターゲット：全て日本人男性。
2. 人称の徹底：キャストのことは必ず「彼女」と呼び、本文中にキャストの名前は絶対に出さないでください。読者は「貴方」と呼ぶこと。
3. 数字の直接表現禁止：本文中で年齢、身長、スリーサイズなどの数字を直接書かないでください（例：「160cm」「22歳」はNG）。
   ただし、「Dカップ」「Fカップ」といったカップ数のみ、魅力の象徴として記載を許可します。
4. 時間帯示唆の完全排除：昼、夜、深夜、ランチ、仕事帰り、太陽、月など、特定の時間帯や外の明るさを連想させる表現は一切禁止。24時間いつでも「非日常空間」であるように執筆すること。
5. 構成：冒頭に【 】で囲んだキャッチコピーを3行。その後に叙情的な本文。
6. 美学：生々しい表現は避け、質感・温度・匂い・情景で魅力を伝えること。
7. ポジティブ変換：いかなる属性も魅力として昇華させること。

【参照お手本】
{samples}

【今回執筆するキャストの情報】
スペック：{full_spec}
特徴：{", ".join(all_selected_keywords)}
"""
            try:
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                with st.spinner("かりんとが傑作データベースからリズムを読み取っています..."):
                    response = client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[{"role": "system", "content": system_prompt}],
                        temperature=0.75
                    )
                    st.session_state.result_text = response.choices[0].message.content.replace("\\n", "\n")
            except Exception as e:
                st.error("APIエラーが発生しました。")

    if st.session_state.result_text:
        st.divider()
        st.header("3. 完成原稿の確認・編集")
        edited_text = st.text_area(
            label="完成原稿（直接編集可能です）",
            value=st.session_state.result_text,
            height=500,
            label_visibility="collapsed"
        )
        
        st.download_button(
            label="修正した内容でテキストを保存",
            data=edited_text,
            file_name=f"profile_{cast_name}.txt",
            use_container_width=True
        )

    st.divider()
    if st.button("ログアウト"):
        st.session_state["authenticated"] = False
        st.rerun()

    st.caption("© かりんと流・プロフ生成ツール ver 2.0 / データベース ver 1.0")
