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
    st.success("Googleスプレッドシートに傑作を追加しました！")

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
    for _, row in best_samples.iterrows():
        body = str(row[content_col]).replace("[改行]", "\n")
        sample_text += f"\n---\n【過去の傑作お手本】\n{body}\n"
    return sample_text

# --- メイン画面 ---
if check_password():
    st.set_page_config(page_title="かりんと流・プロフ生成 ver 3.1", layout="centered")
    
    try:
        conn = get_db_connection()
        db_df = load_data(conn)
    except Exception as e:
        st.error("スプレッドシート接続エラー。Secretsを確認してください。")
        st.stop()

    st.title("✨ かりんと流・プロフ生成 ver 3.1")
    st.caption(f"最高品質の執筆ルールとスプレッドシートDBを統合")

    if "result_text" not in st.session_state:
        st.session_state.result_text = ""

    st.divider()
    st.header("1. キャスト基本情報")
    col_name, col_style = st.columns(2)
    with col_name: cast_name = st.text_input("キャスト名（管理用）", placeholder="例：あやか")
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

    # 執筆実行
    if st.button("✨ かりんと流で執筆を開始する", type="primary", use_container_width=True):
        if not cast_name or not all_selected_keywords:
            st.error("入力を完成させてください。")
        else:
            samples = find_best_samples(db_df, base_style, all_selected_keywords)
            
            # OpenAI APIキーの取得（どちらの形式でも対応）
            if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
                api_key = st.secrets["openai"]["api_key"]
            elif "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
            else:
                st.error("SecretsにAPIキーが見つかりません。")
                st.stop()

            # --- 執筆プロンプト（ver 2.1 の最強版を復刻） ---
            system_prompt = f"""
あなたは日本人女性専門のカリスマライター「かりんと」です。
提供されたデータベースにある「過去の傑作」の文体・リズム・美意識を完璧に継承し、新しいキャストのプロフィールを執筆してください。

【絶対ルール：かりんと流・執筆憲法】
1. ターゲット：全て日本人男性。
2. 人称の徹底：キャストのことは必ず「彼女」と呼び、本文中にキャストの名前は絶対に出さないでください。読者は「貴方」と呼ぶこと。
3. 数字の直接表現禁止：本文中で年齢、身長、スリーサイズなどの数字を直接書かないでください（例：「160cm」「22歳」はNG）。
   ただし、「Dカップ」「Fカップ」といったカップ数のみ、魅力の象徴として記載を許可します。
4. 時間帯示唆の完全排除：昼、夜、深夜、ランチ、仕事帰り、太陽、月など、特定の時間帯や外の明るさを連想させる表現は一切禁止。24時間いつでも、その瞬間が日常から切り離された「二人だけの非日常」に感じられるように執筆すること。
5. 構成：冒頭に【 】で囲んだキャッチコピーを3行。その後に叙情的な本文。
6. 美学：生々しい表現は避け、質感・温度・匂い・情景で魅力を伝えること。
7. ポジティブ変換：いかなる属性も、唯一無二の魅力や官能的な質感としてポジティブに昇華させること。

【参照すべき過去の傑作（お手本）】
{samples}

【今回執筆するキャストの情報】
スペック：{full_spec}
特徴：{", ".join(all_selected_keywords)}
"""
            try:
                client = openai.OpenAI(api_key=api_key)
                with st.spinner("スプレッドシートの傑作から『リズム』を読み取っています..."):
                    response = client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[{"role": "system", "content": system_prompt}],
                        temperature=0.75
                    )
                    st.session_state.result_text = response.choices[0].message.content.replace("\\n", "\n")
            except Exception as e:
                st.error(f"OpenAI APIエラーが発生しました。")

    # 結果表示・編集・登録
    if st.session_state.result_text:
        st.divider()
        st.header("3. 完成原稿の編集・DB登録")
        edited_text = st.text_area("完成原稿（直接編集してスプレッドシートに保存できます）", value=st.session_state.result_text, height=450)
        
        if st.button("📥 この内容をスプレッドシートに直接追加登録する", use_container_width=True):
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

    st.caption("© かりんと流・プロフ生成ツール ver 3.1 / スプレッドシートDB連携中")
