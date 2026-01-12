import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import openai

# --- 1. 定数・キーワード設定 ---
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

# --- 3. スプレッドシート連携 ---
def get_db_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def load_data(conn):
    df = conn.read(ttl="1m")
    df = df.dropna(how="all")
    df.columns = df.columns.str.strip()
    return df

def append_to_sheet(conn, df, new_row):
    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    conn.update(data=updated_df)
    st.success("スプレッドシートに新たな傑作を刻みました。")

# --- 4. お手本検索ロジック ---
def find_best_samples(df, selected_style, selected_keywords):
    if df.empty: return "※お手本なしで執筆します。"
    col_name = "全体の雰囲気" if "全体の雰囲気" in df.columns else df.columns[0]
    filtered_df = df[df[col_name] == selected_style]
    if filtered_df.empty: filtered_df = df
    
    def score_row(row):
        kw_col = "特徴キーワード" if "特徴キーワード" in df.columns else df.columns[1]
        db_kws = str(row[kw_col]).replace(" ", "").split(",")
        return len(set(selected_keywords) & set(db_kws))
    
    filtered_df["score"] = filtered_df.apply(score_row, axis=1)
    best_samples = filtered_df.sort_values(by="score", ascending=False).head(2)
    
    sample_text = ""
    content_col = "該当キャストのプロフ本文" if "該当キャストのプロフ本文" in df.columns else df.columns[-1]
    for i, row in enumerate(best_samples.iterrows()):
        body = str(row[1][content_col]).replace("[改行]", "\n")
        sample_text += f"\n【傑作サンプル {i+1}】\n{body}\n"
    return sample_text

# --- メイン画面 ---
if check_password():
    st.set_page_config(page_title="かりんと流・プロフ生成 ver 3.3", layout="centered")
    
    try:
        conn = get_db_connection()
        db_df = load_data(conn)
    except Exception as e:
        st.error("スプレッドシート接続エラー。")
        st.stop()

    st.title("✨ かりんと流・プロフ生成 ver 3.3")
    st.caption("読者の本能を揺さぶり、昂ぶりを誘発する最終兵器")

    if "result_text" not in st.session_state:
        st.session_state.result_text = ""

    st.divider()
    st.header("1. キャスト基本情報")
    col_name, col_style = st.columns(2)
    with col_name: cast_name = st.text_input("キャスト名（管理用）", placeholder="あやか")
    with col_style: base_style = st.selectbox("ベースとなる系統", STYLES)

    st.subheader("スペック詳細")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: age = st.number_input("年齢", 18, 60, 22)
    with c2: height = st.number_input("身長", 130, 200, 158)
    with c3: bust = st.number_input("バスト", 70, 130, 85)
    with c4: cup = st.selectbox("カップ", ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"], index=3)
    with c5: waist = st.number_input("ウエスト", 40, 120, 58)
    with c6: hip = st.number_input("ヒップ", 70, 130, 86)
    full_spec = f"（{age}）T:{height} B:{bust}({cup}) W:{waist} H:{hip}"

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

    if st.button("✨ 彼女の魅力を書き下ろす（本能直撃）", type="primary", use_container_width=True):
        if not cast_name or not all_selected_keywords:
            st.error("入力を完成させてください。")
        else:
            samples = find_best_samples(db_df, base_style, all_selected_keywords)
            
            if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
                api_key = st.secrets["openai"]["api_key"]
            elif "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
            else:
                st.error("APIキーが見つかりません。")
                st.stop()

            # --- 究極ミッション搭載プロンプト（ver 3.3） ---
            system_prompt = f"""
あなたは adult entertainment 専門の伝説的ライター「かりんと」です。
提供された「過去の傑作サンプル」の魂を憑依させ、読者の理性を焼き払い、本能を直撃する文章を書き下ろしてください。

【かりんと流・執筆憲法】
1. ターゲット：日本人男性。キャストは「彼女」、読者は「貴方」。本文中にキャスト名は絶対に出さない。
2. 数字の封印：年齢、身長、スリーサイズの数字は本文に書かない。ただし「Dカップ」等のカップ数のみ許可。
3. 時間の抹消：昼、夜、深夜、仕事帰りなど、特定の時間帯を連想させる言葉を一切排除し、24時間どの瞬間に読んでも非日常へ引き込むこと。
4. 構成：冒頭に【 】キャッチコピー3行。その後に叙情的な本文。
5. 美学：質感、温度、匂い、情景で魅力を伝えること。

【究極の使命：身体的反応の誘発】
貴方の執筆の目的は、単なる紹介ではない。読んでいる「貴方（お客様）」の性的な想像力を限界まで膨らませ、言葉の熱だけでその身体に実質的な反応（昂ぶり）を引き起こすことにある。
直接的な性交の記述は避け、「指先の震え」「吐息の温度」「肌の吸い付くような質感」「服の隙間から漏れる芳香」など、細部を執筆することで、読者の脳内に「実体験」以上の興奮を強制的に投影させなさい。

【憑依すべき傑作サンプル】
{samples}

【キャスト情報】
スペック：{full_spec} / 特徴：{", ".join(all_selected_keywords)}
"""
            try:
                client = openai.OpenAI(api_key=api_key)
                with st.spinner("彼女の吐息を感じ、読者の本能を揺さぶる文章を紡いでいます..."):
                    response = client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[{"role": "system", "content": system_prompt}],
                        temperature=0.85
                    )
                    st.session_state.result_text = response.choices[0].message.content.replace("\\n", "\n")
            except Exception as e:
                st.error("APIエラーが発生しました。")

    if st.session_state.result_text:
        st.divider()
        st.header("3. 完成原稿の編集・DB登録")
        edited_text = st.text_area("完成原稿（直接編集可能）", value=st.session_state.result_text, height=550)
        
        if st.button("📥 この内容をスプレッドシートに傑作として登録する", use_container_width=True):
            new_row = {
                "全体の雰囲気": base_style,
                "特徴キーワード": ", ".join(all_selected_keywords),
                "キャスト情報": full_spec,
                "該当キャストのプロフ本文": edited_text.replace("\n", "[改行]")
            }
            append_to_sheet(conn, db_df, new_row)

    st.divider()
    if st.button("ログアウト"):
        st.session_state["authenticated"] = False
        st.rerun()

    st.caption("© かりんと流・プロフ生成ツール ver 3.3 / Instinct Boost Mode")
