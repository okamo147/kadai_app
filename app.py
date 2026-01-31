import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. アプリの説明 (必須条件①)
st.title("e-Stat 人口統計可視化アプリ")
st.caption("e-Statからダウンロードした「年齢各歳別人口」データを分析します。")

# 2. データの読み込み
# 事前にGitHubリポジトリに CSVファイルをアップロードしておく必要があります
file_path = "FEH_00200524_260131155049.csv"

try:
    df_raw = pd.read_csv(file_path, encoding="utf-8") # e-StatのCSVは通常UTF-8
    
    # サイドバー設定 (必須条件①)
    st.sidebar.header("表示設定")
    
    # 未使用UI部品①: st.color_picker
    line_color = st.sidebar.color_picker("グラフの色を選択", "#1f77b4")

    # データ抽出（「男女計」「総人口」かつ「総数(01000)以外」を抽出）
    # CSVの列名に合わせてフィルタリング
    df = df_raw[
        (df_raw["男女別・性比"] == "男女計") & 
        (df_raw["人口"] == "総人口") & 
        (df_raw["年齢各歳"] != "総数")
    ].copy()

    # 年齢（年齢各歳）を数値に変換（例：「0歳」→ 0）
    df["age_num"] = df["年齢各歳"].str.extract('(\[0-9\]+)').astype(float)
    df["value"] = pd.to_numeric(df["value"], errors='coerce')

    # 時間軸（調査年）の選択 (必須条件①: 条件変更)
    years = df["時間軸（年月日現在）"].unique()
    selected_year = st.sidebar.selectbox("調査年を選択してください", years)

    # 選択された年のデータを抽出
    df_year = df[df["時間軸（年月日現在）"] == selected_year].sort_values("age_num")

    # 3. 可視化 (必須条件①: 2種類以上)
    st.subheader(f"{selected_year} 年齢別人口分布")

    # グラフ1: Matplotlib (折れ線グラフ)
    fig, ax = plt.subplots()
    ax.plot(df_year["age_num"], df_year["value"], color=line_color)
    ax.set_xlabel("年齢")
    ax.set_ylabel("人口（千人）")
    st.pyplot(fig)

    # グラフ2: Streamlit標準の棒グラフ (必須条件①)
    # 未使用UI部品②: st.bar_chart
    st.write("年齢別人口（棒グラフ）")
    st.bar_chart(df_year.set_index("年齢各歳")["value"])

    # 4. データ表示
    # 未使用UI部品③: st.expander（詳細を隠しておく機能）
    with st.expander("詳細データ表を確認"):
        st.dataframe(df_year[["年齢各歳", "value"]].style.highlight_max(axis=0))

    # 5. 分析・考察 (必須条件①)
    st.info("単位：千人")
    st.write("### 【分析結果の考察】")
    st.write(f"{selected_year}のデータを見ると、特定の年齢層（団塊の世代や団塊ジュニア世代など）にボリュームゾーンがあることがわかります。")

    # 6. ダウンロードボタン
    st.sidebar.download_button(
        label="加工済みデータを保存",
        data=df_year.to_csv(index=False).encode('utf_8_sig'),
        file_name=f'population_{selected_year}.csv',
        mime='text/csv',
    )

except FileNotFoundError:
    st.error(f"エラー: {file_path} が見つかりません。GitHubにCSVファイルをアップロードしてください。")
except Exception as e:
    st.error(f"予期せぬエラーが発生しました: {e}")