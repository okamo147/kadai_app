import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("e-Stat 人口統計可視化アプリ")

# GitHub上のファイル名と一致させてください
file_path = "FEH_00200524_260131160542.csv"

try:
    # 修正ポイント：e-Statの全項目引用符付きCSVを確実に読み込む設定
    df_raw = pd.read_csv(
        file_path, 
        quotechar='"',          # 引用符は "
        skipinitialspace=True,  # 空白を飛ばす
        on_bad_lines='warn'     # おかしな行があっても止まらずに警告を出す
    )
    
    # 列名の空白削除
    df_raw.columns = df_raw.columns.str.strip()

    # データ抽出の条件
    # CSVの中身を確認し、「男女計」「総人口」かつ年齢が「総数」以外を抽出
    df = df_raw[
        (df_raw["男女別・性比"] == "男女計") & 
        (df_raw["人口"] == "総人口") & 
        (~df_raw["年齢各歳"].isin(["総数", "（再掲）不詳"]))
    ].copy()

    # 数値変換（value列の型を整える）
    df["value"] = pd.to_numeric(df["value"], errors='coerce')

    # 年齢の数字だけを取り出す（例：「0歳」→ 0）
    df["age_num"] = df["年齢各歳"].str.extract(r'(\d+)').astype(float)

    # 調査年を選択
    years = df["時間軸（年月日現在）"].unique()
    selected_year = st.sidebar.selectbox("調査年を選択", years)

    # 選択年のデータを取得
    df_year = df[df["時間軸（年月日現在）"] == selected_year].sort_values("age_num")

    # 可視化：Matplotlib
    st.subheader(f"{selected_year} 年齢別人口分布")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_year["age_num"], df_year["value"], color="teal", marker='o', markersize=3)
    ax.set_xlabel("年齢")
    ax.set_ylabel("人口（千人）")
    st.pyplot(fig)

    # 可視化：エリアチャート
    st.write("人口推移（エリアチャート）")
    st.area_chart(df_year.set_index("年齢各歳")["value"])

    # 詳細表示
    with st.expander("詳細データ表を確認"):
        st.dataframe(df_year[["年齢各歳", "value"]].style.highlight_max(axis=0))

    st.info("単位：千人")

except Exception as e:
    st.error(f"エラーが発生しました: {e}")
    # ログ出力用
    st.write("CSVの列名一覧:", df_raw.columns.tolist() if 'df_raw' in locals() else "読み込み失敗")