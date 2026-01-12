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

# --- 2. CSS注入（デザインのコンパクト化） ---
st.markdown("""
    <style>
    .main-title { font-size: 1.4rem !important; font-weight: bold; margin-bottom: 0.5rem; color: #333; }
    .section-head { font-size: 1.0rem !important; font-weight: bold; margin-top: 1.0rem; margin-bottom: 0.2rem; color: #555; }
    .spec-head { font-size: 0.9rem !important; font-weight: bold; margin-bottom: 0.1rem; color: #777; }
    .block-container { padding-top: 2rem !important; }
    div[data-baseweb="input"] { font-size: 0.9rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 認証機能 ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.markdown('<p class="main-title">🔐 かりんと流 ログイン</p>', unsafe_allow_html=True)
        password = st.text_input("パスワードを入力してください", type="password")
        if st.button("ログイン"):
            if password == "karin10":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("パスワードが違います。")
        return False
    return True

# --- 4. スプレッドシート連携 ---
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
    st.success("スプレッドシートに傑作を保存しました。")

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
    st.set_page_config(page_title="かりんと流・プロフ生成 ver 4.0", layout="centered")
    try:
        conn = get_db_connection()
        db_df = load_data(conn)
    except:
        st.error("スプレッドシート接続エラー。")
        st.stop()

    st.markdown(f'<p class="main-title">✨ かりんと流・プロフ生成 ver 4.0</p>', unsafe_allow_html=True)
    st.caption(f"DB同期済み: {len(db_df)}名の傑作データを参照中")

    if "result_text" not in st.session_state:
        st.session_state.result_text = ""

    st.divider()
    st.markdown('<p class="section-head">1. キャスト基本情報</p>', unsafe_allow_html=True)
    c_name, c_style = st.columns(2)
    with c_name: cast_name = st.text_input("キャスト名", placeholder="あやか")
    with c_style: base_style = st.selectbox("ベース系統", STYLES)

    st.markdown('<p class="spec-head">スペック詳細（±ボタンで調整可）</p>', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    with s1: age = st.number_input("年齢", 18, 60, 22, step=1)
    with s2: height = st.number_input("身長", 130, 200, 158, step=1)
    with s3: cup = st.selectbox("カップ", ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"], index=3)
    s4, s5, s6 = st.columns(3)
    with s4: bust = st.number_input("バスト", 70, 130, 85, step=1)
    with s5: waist = st.number_input("ウエスト", 40, 120, 58, step=1)
    with s6: hip = st.number_input("ヒップ", 70, 130, 86, step=1)
    full_spec = f"（{age}）T:{height} B:{bust}({cup}) W:{waist} H:{hip}"

    st.divider()
    st.markdown('<p class="section-head">2. 特徴タグの選択</p>', unsafe_allow_html=True)
    all_selected_keywords = []
    def create_grid(label, options, prefix):
        st.markdown(f"**{label}**")
        cols = st.columns(4)
        selected = []
        for i, opt in enumerate(options):
            if cols[i%4].checkbox(opt, key=f"{prefix}_{opt}"): selected.append(opt)
        return selected
    all_selected_keywords += create_grid("●タイプ", TYPES, "t")
    all_selected_keywords += create_grid("●ルックス", LOOKS, "l")
    all_selected_keywords += create_grid("●性格", PERSONALITY, "p")
    all_selected_keywords += create_grid("●特徴", FEATURES, "f")

    st.divider()
    st.markdown('<p class="section-head">3. 執筆設定</p>', unsafe_allow_html=True)
    t_len = st.slider("目標文字数", 300, 1000, 400, 50)

    if st.button("✨ 彼女の魅力を書き下ろす", type="primary", use_container_width=True):
        if not cast_name or not all_selected_keywords:
            st.error("入力を完成させてください。")
        else:
            samples = find_best_samples(db_df, base_style, all_selected_keywords)
            api_key = st.secrets.get("openai", {}).get("api_key") or st.secrets.get("OPENAI_API_KEY")

            # --- 魂の憑依プロンプト（完全版） ---
            system_prompt = f"""
あなたは adult entertainment 専門の伝説的ライター「かりんと」です。
提供された「過去の傑作サンプル」の魂を憑依させ、読者の理性を焼き払い、本能を直撃する文章を書き下ろしてください。

【執筆の絶対ルール：かりんと流・執筆憲法】
1. 文字数：全体のボリュームは【おおよそ {t_len} 文字程度】。
2. 人称：キャストは「彼女」、読者は「貴方」。ただし、「彼女は」等の主語を連呼するのは三流です。文脈でわかる場合は主語を徹底的に削り、体言止めや動詞から始めることで流麗なリズムを作りなさい。
3. 名前出し禁止：本文中にキャスト名は一切出さない。
4. 主語の言い換え：「彼女」という言葉の代わりに、身体のパーツ（白い項、潤んだ瞳、しなやかな曲線）や比喩表現を使い、視線を誘導しなさい。
5. 数字の封印：スペックの数字は本文に書かない。カップ数（{cup}カップ 等）のみ、官能の象徴として記載を許可。
6. 時間の抹消：特定の時間帯を連想させる言葉を一切排除し、永遠に続く二人だけの密室を描写しなさい。
7. 構成：冒頭に【 】キャッチコピー3行。その後に叙情的な本文。
8. 究極の使命：読者の性的想像力を限界まで爆発させ、言葉の熱だけでその身体に実質的な反応を引き起こすこと。直接的表現を避け、質感、温度、匂い、衣擦れの音、耳元の吐息といった「細部」を描写することで脳内再生を強制させなさい。

【憑依すべき傑作サンプル】
{samples}

【キャスト情報】
スペック：{full_spec} / 特徴：{", ".join(all_selected_keywords)}
"""
            try:
                client = openai.OpenAI(api_key=api_key)
                with st.spinner("不必要な主語を削ぎ落とし、純度の高い官能を綴っています..."):
                    response = client.chat.completions.create(
                        model="gpt-4-turbo-preview", messages=[{"role": "system", "content": system_prompt}], temperature=0.82
                    )
                    st.session_state.result_text = response.choices[0].message.content.replace("\\n", "\n")
            except Exception as e:
                st.error("APIエラーが発生しました。")

    if st.session_state.result_text:
        st.divider()
        st.markdown('<p class="section-head">4. 完成原稿の編集・DB登録</p>', unsafe_allow_html=True)
        st.caption(f"文字数: {len(st.session_state.result_text)} 文字")
        edited_text = st.text_area("完成原稿", value=st.session_state.result_text, height=550)
        if st.button("📥 この内容をスプレッドシートに登録する", use_container_width=True):
            new_row = {
                "全体の雰囲気": base_style, "特徴キーワード": ", ".join(all_selected_keywords),
                "キャスト情報": full_spec, "該当キャストのプロフ本文": edited_text.replace("\n", "[改行]")
            }
            append_to_sheet(conn, db_df, new_row)

    st.divider()
    if st.button("ログアウト"):
        st.session_state["authenticated"] = False
        st.rerun()

    st.caption("© かりんと流・プロフ生成 ver 4.0")
