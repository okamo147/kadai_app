import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. アプリの説明
st.title("e-Stat 人口統計可視化アプリ")
st.caption("e-Statの「年齢各歳別人口」データを分析します。")

# 2. データの読み込み
# アップロードしたファイル名と完全に一致させる
file_path = "FEH_00200524_260131160542.csv"

try:
    # 修正ポイント①: e-StatのCSVは1行目が説明文の場合があるため
    # header=0 で読み込み、エラーが出る場合はその後の処理で列名を整える
    df_raw = pd.read_csv(file_path, quotechar='"', skipinitialspace=True)
    
    # 列名の空白を削除
    df_raw.columns = df_raw.columns.str.strip()

    # 3. データの加工 (必須条件①)
    # 修正ポイント②: 「男女計」「総人口」で絞り込み、かつ年齢が数値化できるもの
    # 確実に存在する列名であることを確認しつつ処理
    target_sex = "男女計"
    target_pop = "総人口"
    
    df = df_raw[
        (df_raw["男女別・性比"] == target_sex) & 
        (df_raw["人口"] == target_pop) & 
        (~df_raw["年齢各歳"].isin(["総数", "（再掲）不詳"]))
    ].copy()

    # 年齢の数値化（「0歳」→ 0）
    df["age_num"] = df["年齢各歳"].str.extract(r'(\d+)').astype(float)
    df["value"] = pd.to_numeric(df["value"], errors='coerce')

    # サイドバー：調査年選択
    years = df["時間軸（年月日現在）"].unique()
    selected_year = st.sidebar.selectbox("調査年を選択してください", years)
    
    # 色選択 (未使用UI部品①)
    line_color = st.sidebar.color_picker("グラフの色を選択", "#1f77b4")

    # 選択された年のデータを抽出
    df_year = df[df["時間軸（年月日現在）"] == selected_year].sort_values("age_num")

    # 4. 可視化 (2種類以上)
    st.subheader(f"{selected_year} 年齢別人口分布")

    # グラフ1: Matplotlib (折れ線)
    fig, ax = plt.subplots()
    ax.plot(df_year["age_num"], df_year["value"], color=line_color, marker='o', markersize=3)
    ax.set_xlabel("年齢")
    ax.set_ylabel("人口（千人）")
    st.pyplot(fig)

    # グラフ2: Streamlit Area Chart (未使用UI部品②)
    st.write("年齢別人口（エリアチャート）")
    st.area_chart(df_year.set_index("年齢各歳")["value"])

    # 5. データ表示 (未使用UI部品③)
    with st.expander("詳細データ表を確認"):
        st.dataframe(df_year[["年齢各歳", "value"]].style.highlight_max(axis=0))

    # 単位と考察
    st.info("単位：千人")
    st.write("### 【分析結果の考察】")
    st.write(f"{selected_year}のデータを確認すると、特定の年齢層にピークがあり、少子高齢化の傾向が視覚的に把握できます。")

    # 6. ダウンロードボタン
    st.sidebar.download_button(
        label="加工済みデータを保存",
        data=df_year.to_csv(index=False).encode('utf_8_sig'),
        file_name=f'population_{selected_year}.csv',
        mime='text/csv',
    )

except FileNotFoundError:
    st.error(f"エラー: {file_path} が見つかりません。GitHubに正しいファイル名でアップロードしてください。")
except KeyError as e:
    st.error(f"エラー: CSVの列名が見つかりません。列名を確認してください。 {e}")
except Exception as e:
    st.error(f"エラーが発生しました: {e}")