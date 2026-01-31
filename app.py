import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# 1. アプリの説明 (必須条件①: UI)
st.title("e-Stat 統計データ可視化アプリ")
st.caption("政府統計ポータルサイト e-Stat の統計ダッシュボードAPIを利用しています。")
st.write("このアプリでは、指定した地域の人口推移をグラフで確認できます。") # [cite: 58]

# 2. サイドバーでの条件設定 (必須条件①: 機能)
st.sidebar.header("表示設定") # [cite: 57]

# 未使用UI部品①: st.color_picker (必須条件②)
# 目的: ユーザーが好みの色で可視化を行えるようにするため
line_color = st.sidebar.color_picker("グラフの線の色を選択", "#00f900") # [cite: 74, 79]

# 都道府県の選択 (必須条件①: 条件変更)
region_code = st.sidebar.selectbox(
    "地域を選択してください",
    options=["13", "01", "27"],
    format_func=lambda x: {"13": "東京都", "01": "北海道", "27": "大阪府"}.get(x)
) # [cite: 59]

# 3. データ取得処理 (e-Stat API)
url = "https://dashboard.e-stat.go.jp/api/1.0/Json/getIndicatorData"
params = {
    "indicatorCode": "0301010001010010010030301",  # 人口（系列コード）
    "regionCode": region_code,
    "startYear": "1990",
    "endYear": "2020",
    "format": "json"
}

try:
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        
        # JSONから数値を抽出（データが存在するかチェック）
        indicator_data = data.get("IndicatorData", [])
        if indicator_data:
            values = indicator_data[0].get("DataValue", [])
            df = pd.DataFrame(values)

            # データ型の変換
            df["@time"] = pd.to_datetime(df["@time"], format="%Y")
            df["$"] = pd.to_numeric(df["$"])

            # 4. 可視化 (必須条件①: 最低2種類の表示)
            st.subheader("可視化結果")

            # --- グラフ1: Matplotlibを使用した折れ線グラフ ---
            fig, ax = plt.subplots()
            ax.plot(df["@time"], df["$"], color=line_color, marker='o')
            ax.set_xlabel("年")
            ax.set_ylabel("人口（人）")
            ax.set_title("人口推移グラフ")
            st.pyplot(fig) # [cite: 61, 172]

            # --- グラフ2: Streamlit標準の面グラフ (Area Chart) ---
            # 未使用UI部品②: st.area_chart
            # 目的: 塗りつぶしによる視覚的な変化を比較するため
            st.write("人口推移（エリアチャート）")
            st.area_chart(df.set_index("@time")["$"]) # [cite: 74]

            # --- データテーブル表示 ---
            st.write("詳細データ一覧")
            # 未使用UI部品③: st.dataframe の highlight 機能
            st.dataframe(df.style.highlight_max(axis=0), use_container_width=True) # [cite: 74]

            # 5. 解釈と単位の明示 (必須条件①)
            st.info("単位：人") # [cite: 65, 68]
            st.write("【分析結果の考察】")
            st.write("グラフから、選択した地域の人口増減の傾向を読み取ることができます。") # [cite: 64, 149]

            # 6. CSVダウンロードボタン (ここで定義すれば NameError は起きない)
            st.sidebar.download_button(
                label="CSVをダウンロード",
                data=df.to_csv(index=False).encode('utf_8_sig'),
                file_name='estat_data.csv',
                mime='text/csv',
            )
        else:
            st.warning("データが見つかりませんでした。")
    else:
        st.error(f"APIエラー: {response.status_code}")

except Exception as e:
    st.error(f"エラーが発生しました: {e}")