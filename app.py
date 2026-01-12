import streamlit as st
import pandas as pd
import openai

# --- 1. 定数・キーワード設定（36項目） ---
STYLES = ["清楚・可憐", "妖艶・色香", "親近感・ナチュラル", "都会的・洗練", "天真爛漫・愛嬌", "女子アナ風・気品", "地雷・量産型トレンド"]

TYPES = ["清楚", "癒し系", "綺麗系", "可愛い系", "ロリ系", "ギャル系", "モデル系", "お姉さん系"]
LOOKS = ["スレンダー", "セクシー", "グラマー", "巨乳", "微乳", "美肌", "色白", "美乳", "美脚", "美尻"]
PERSONALITY = ["明るい", "甘えん坊", "ツンデレ", "恥ずかしがり屋", "人懐っこい", "愛嬌抜群", "しっかり者", "聞き上手", "天然", "オタク", "おっとり"]
FEATURES = ["黒髪", "完全未経験", "処女", "スタイル抜群", "テクニシャン", "責め好き", "エッチ好き"]

# --- 2. データベース読み込み機能 ---
@st.cache_data
def load_database():
    """
    GitHub上に配置した database.csv (28名分の傑作データ) を読み込む。
    形式はタブ区切り(TSV)を想定。
    """
    try:
        # 先ほど整理した28件のデータを database.csv としてルートに置く
        df = pd.read_csv("database.csv", sep="\t")
        return df
    except Exception as e:
        st.error(f"データベースファイル(database.csv)の読み込みに失敗しました: {e}")
        return None

# --- 3. お手本検索ロジック ---
def find_best_samples(df, selected_style, selected_keywords):
    if df is None or df.empty:
        return "※お手本データが読み込めなかったため、基本ルールのみで執筆します。"
    
    # 1. まず「系統（A列）」で絞り込み
    filtered_df = df[df["全体の雰囲気"] == selected_style]
    if filtered_df.empty:
        filtered_df = df # 該当スタイルがない場合は全体から検索
    
    # 2. キーワード（B列）の一致数でスコアリング
    def score_row(row):
        db_kws = str(row["特徴キーワード"]).replace(" ", "").split(",")
        # 入力されたキーワードとデータベースのキーワードの重複数を計算
        return len(set(selected_keywords) & set(db_kws))
    
    filtered_df["score"] = filtered_df.apply(score_row, axis=1)
    # スコアが高い順に最大2件を抽出
    best_samples = filtered_df.sort_values(by="score", ascending=False).head(2)
    
    sample_text = ""
    for _, row in best_samples.iterrows():
        sample_text += f"\n---\n【過去の傑作お手本】\n{row['該当キャストのプロフ本文']}\n"
    
    return sample_text

# --- 4. UI 構築 ---
st.set_page_config(page_title="かりんと流・プロフ生成 ver 1.2.1", layout="wide")
st.title("✨ かりんと流・プロフ生成ツール ver 1.2.1")
st.caption("28名の傑作データベースを元に、最高品質のプロフを書き下ろします。")

with st.sidebar:
    st.header("1. キャスト情報入力")
    cast_name = st.text_input("キャスト名", placeholder="例：あやか")
    cast_spec = st.text_area("スペック詳細", placeholder="例：（20）T:158 B:88(E) W:58 H:86", height=100)
    
    st.header("2. 雰囲気・タグ選択")
    base_style = st.selectbox("ベースとなる系統（全体の雰囲気）", STYLES)
    
    st.subheader("●タイプ")
    sel_types = st.multiselect("タイプを選択", TYPES)
    st.subheader("●ルックス")
    sel_looks = st.multiselect("ルックスを選択", LOOKS)
    st.subheader("●性格")
    sel_personality = st.multiselect("性格を選択", PERSONALITY)
    st.subheader("●特徴・個性")
    sel_features = st.multiselect("特徴を選択", FEATURES)
    
    all_selected_keywords = sel_types + sel_looks + sel_personality + sel_features

# --- 5. メイン実行エリア ---
if st.button("かりんと流で執筆を開始する", type="primary"):
    if not cast_spec or not all_selected_keywords:
        st.error("スペック情報とキーワードを少なくとも1つずつ選択してください。")
    else:
        # データベースからお手本を抽出
        db = load_database()
        samples = find_best_samples(db, base_style, all_selected_keywords)
        
        # プロンプト構築（ver 1.2.1 改訂版）
        system_prompt = f"""
あなたは日本人女性専門のカリスマライター「かりんと」です。
提供されたデータベースにある「過去の傑作」の文体・リズム・美意識を完璧に継承し、新しいキャストのプロフィールを執筆してください。

【絶対ルール：かりんと流・執筆憲法】
1. ターゲット：全て日本人男性。
2. 人称：キャストは「彼女」、読者は「貴方」と呼ぶこと。
3. 時間帯示唆の完全排除（最重要）：
   昼、夜、深夜、仕事帰り、太陽、月など、特定の時間帯や明るさを連想させる表現は一切使わないでください。
   24時間いつ読んでも、その瞬間が「日常から切り離された非日常」に感じられるように執筆すること。
4. 時間の表記：「時」または「刻」という言葉は自由に使ってよいが、時間帯を特定しないこと。
5. 構成：冒頭に【 】で囲んだキャッチコピーを3行。その後に叙情的な本文。
6. 美学：生々しい直接的表現は避け、質感・温度・匂い・情景で官能を表現すること。
7. ポジティブ変換：ギャルやふくよかな体型などは、唯一無二のギャップや官能的な質感として魅力的に昇華させること。

【参照すべき過去の傑作（お手本）】
{samples}

【今回執筆するキャストの情報】
名前：{cast_name}
スペック：{cast_spec}
特徴：{", ".join(all_selected_keywords)}
"""

        # OpenAI API 呼び出し
        try:
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            
            with st.spinner("かりんとが傑作データベースからリズムを読み取っています..."):
                response = client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "system", "content": system_prompt}],
                    temperature=0.75
                )
                
                result_text = response.choices[0].message.content
                
                # 結果表示
                st.divider()
                st.subheader(f"✨ {cast_name} さんの完成原稿")
                st.markdown(result_text)
                st.download_button("原稿をテキスト保存", result_text, file_name=f"profile_{cast_name}.txt")
                
        except Exception as e:
            st.error(f"生成エラーが発生しました。APIキーの設定などを確認してください: {e}")

# --- フッター ---
st.caption("© かりんと流・プロフ生成ツール ver 1.2.1 / データベース ver 1.0 連携済み")
