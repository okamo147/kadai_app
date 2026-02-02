import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("e-Stat 人口統計可視化アプリ")
st.caption("e-Statのデータを元に年齢別人口を分析します。")

file_path = "FEH_00200524_260131160542.csv"

try:

    df_raw = pd.read_csv(
        file_path, 
        skiprows=12,   
        quotechar='"', 
        encoding="utf-8"
    )
    
    df_raw.columns = df_raw.columns.str.strip()

    if "年齢各歳" not in df_raw.columns:
        df_raw = pd.read_csv(file_path, skiprows=13, quotechar='"', encoding="utf-8")
        df_raw.columns = df_raw.columns.str.strip()

    df = df_raw[
        (~df_raw["年齢各歳"].isin(["総数", "（再掲）不詳", "不詳"])) & 
        (df_raw["年齢各歳"].notna()) &
        (df_raw["年齢各歳"] != "年齢各歳") 
    ].copy()

    df["value"] = pd.to_numeric(df["男女計【千人】"].astype(str).str.replace(',', ''), errors='coerce')
    df["age_num"] = df["年齢各歳"].str.extract(r'(\d+)').astype(float)

    years = df["時間軸（年月日現在）"].unique()
    selected_year = st.sidebar.selectbox("調査年を選択", years)
    df_year = df[df["時間軸（年月日現在）"] == selected_year].sort_values("age_num")

    st.subheader(f"Population Distribution ({selected_year})")
    
    line_color = st.sidebar.color_picker("グラフの色を選択", "#0077ff")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_year["age_num"], df_year["value"], color=line_color, marker='o', markersize=2)
    
    ax.set_xlabel("Age")
    ax.set_ylabel("Population (x1000)")
    
    st.pyplot(fig)

    st.write("年齢別人口（エリアチャート）")
    st.area_chart(df_year.set_index("年齢各歳")["value"])

    with st.expander("詳細データ表を確認"):
        st.dataframe(df_year[["年齢各歳", "男女計【千人】"]].style.highlight_max(axis=0))

except Exception as e:
    st.error(f"起動エラーが発生しました: {e}")
    if 'df_raw' in locals():
        st.write("現在の列名:", df_raw.columns.tolist())