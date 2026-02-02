import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("e-Stat 人口統計可視化アプリ")
st.caption("詳細な年齢別人口データを可視化します。")

file_path = "FEH_00200524_260131160542.csv"

try:
    df_raw = pd.read_csv(
        file_path, 
        skiprows=14,  
        quotechar='"', 
        encoding="utf-8" 
    )
    
    df_raw.columns = df_raw.columns.str.strip()


    df = df_raw[
        (~df_raw["年齢各歳"].isin(["総数", "（再掲）不詳", "不詳"])) & 
        (df_raw["年齢各歳"].notna())
    ].copy()

    df["value"] = pd.to_numeric(df["男女計【千人】"].astype(str).str.replace(',', ''), errors='coerce')

    df["age_num"] = df["年齢各歳"].str.extract(r'(\d+)').astype(float)

    years = df["時間軸（年月日現在）"].unique()
    selected_year = st.sidebar.selectbox("調査年を選択", years)

    df_year = df[df["時間軸（年月日現在）"] == selected_year].sort_values("age_num")

    st.subheader(f"{selected_year} 年齢別人口分布")
    
    line_color = st.sidebar.color_picker("グラフの色を選択", "#0077ff")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_year["age_num"], df_year["value"], color=line_color, marker='o', markersize=2)
    ax.set_xlabel("Age")
    ax.set_ylabel("Population (1000s)")
    st.pyplot(fig)

    st.write("人口推移（エリアチャート）")
    st.area_chart(df_year.set_index("年齢各歳")["value"])

    with st.expander("詳細データ表を確認"):
        st.dataframe(df_year[["年齢各歳", "男女計【千人】", "男【千人】", "女【千人】"]].style.highlight_max(axis=0))

    st.info("単位：千人")

except Exception as e:
    st.error(f"エラーが発生しました: {e}")
    if 'df_raw' in locals():
        st.write("読み込まれた列名一覧:", df_raw.columns.tolist())