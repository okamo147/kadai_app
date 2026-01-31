import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("e-Stat 人口統計可視化アプリ")
st.caption("詳細な年齢別人口データを可視化します。")

# GitHub上のファイル名と一致させてください
file_path = "FEH_00200524_260131160542.csv"

try:
    # 修正ポイント①: 最初の説明行（メタデータ）をスキップして読み込む
    # このCSVは15行目あたりから実際のデータが始まっているため skiprows を使用
    df_raw = pd.read_csv(
        file_path, 
        skiprows=14,  # 14行目まで飛ばしてヘッダーを読み込む
        quotechar='"', 
        encoding="utf-8"
    )
    
    # 列名の空白削除
    df_raw.columns = df_raw.columns.str.strip()

    # 修正ポイント②: 「年齢各歳」が「総数」以外の行に絞り込む
    # このCSVでは「男女計【千人】」がデータ列になります
    df = df_raw[
        (~df_raw["年齢各歳"].isin(["総数", "（再掲）不詳", "不詳"])) & 
        (df_raw["年齢各歳"].notna())
    ].copy()

    # 数値変換（「男女計【千人】」列を使用。カンマが含まれる場合は削除）
    df["value"] = pd.to_numeric(df["男女計【千人】"].astype(str).str.replace(',', ''), errors='coerce')

    # 年齢の数字だけを取り出す
    df["age_num"] = df["年齢各歳"].str.extract(r'(\d+)').astype(float)

    # 調査年を選択
    years = df["時間軸（年月日現在）"].unique()
    selected_year = st.sidebar.selectbox("調査年を選択", years)

    # 選択年のデータを取得
    df_year = df[df["時間軸（年月日現在）"] == selected_year].sort_values("age_num")

    # 可視化
    st.subheader(f"{selected_year} 年齢別人口分布")
    
    # 未使用UI部品①: st.color_picker
    line_color = st.sidebar.color_picker("グラフの色を選択", "#0077ff")

    # グラフ1: Matplotlib
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_year["age_num"], df_year["value"], color=line_color, marker='o', markersize=2)
    ax.set_xlabel("年齢")
    ax.set_ylabel("人口（千人）")
    st.pyplot(fig)

    # グラフ2: エリアチャート (未使用UI部品②)
    st.write("人口推移（エリアチャート）")
    st.area_chart(df_year.set_index("年齢各歳")["value"])

    # 詳細表示 (未使用UI部品③)
    with st.expander("詳細データ表を確認"):
        st.dataframe(df_year[["年齢各歳", "男女計【千人】", "男【千人】", "女【千人】"]].style.highlight_max(axis=0))

    st.info("単位：千人")

except Exception as e:
    st.error(f"エラーが発生しました: {e}")
    # 読み込みに失敗した際、列名を確認するためのデバッグ情報
    if 'df_raw' in locals():
        st.write("読み込まれた列名一覧:", df_raw.columns.tolist())