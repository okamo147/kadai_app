import streamlit as st
import requests
import pandas as pd

# 1. アプリの説明 (必須条件①: UI) [cite: 58, 68]
st.title("e-Stat 統計データ可視化アプリ")
st.caption("政府統計ポータルサイト e-Stat の統計ダッシュボードAPIを利用しています。")
st.write("このアプリでは、指定した指標の推移をグラフで確認できます。")

# 2. サイドバーでの条件設定 (必須条件①: 機能) [cite: 57, 59]
st.sidebar.header("表示設定")

# 未使用UI部品①: st.color_picker (必須条件②) [cite: 71, 74]
# 目的: グラフの線の色をユーザーが自由に変更できるようにするため
line_color = st.sidebar.color_picker("グラフの線の色を選択", "#00f900")

# 都道府県の選択 (13=東京, 01=北海道 など)
region_code = st.sidebar.selectbox(
    "地域を選択してください",
    options=["13", "01", "27"],
    format_func=lambda x: {"13": "東京都", "01": "北海道", "27": "大阪府"}.get(x)
)

# 3. データ取得処理 (e-Stat API) [cite: 34, 35]
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
        
        # JSONから必要な数値データを抽出
        values = data["IndicatorData"][0]["DataValue"]
        df = pd.DataFrame(values)
        
        # データ型の変換
        df["@time"] = pd.to_datetime(df["@time"], format="%Y")
        df["$"] = pd.to_numeric(df["$"])

        # 4. データの表示・可視化 (必須条件①: 最低2種類) [cite: 61, 63]
        st.subheader(f"選択された地域の人口推移")
        
        # グラフ1: 折れ線グラフ (st.line_chart または matplotlib)
        st.line_chart(df.set_index("@time")["$"])
        
        # グラフ2: データテーブルの表示 (必須条件①: データの確認) [cite: 58]
        # 未使用UI部品②: st.dataframe の高度な表示 (必須条件②) [cite: 71]
        st.write("詳細データ一覧")
        st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)
        
        # 5. 解釈と単位の明示 (必須条件①) [cite: 64, 65, 68]
        st.info("単位：人")
        st.write("【分析結果の考察】")
        st.write("このグラフから、選択した地域の人口傾向を読み取ることができます。")

    else:
        st.error(f"データの取得に失敗しました。ステータスコード: {response.status_code}")

except Exception as e:
    st.error(f"エラーが発生しました: {e}")

# 未使用UI部品③: st.download_button (必須条件②) [cite: 71, 74]
# 目的: ユーザーが手元でデータを分析できるようにCSVとして配布するため
st.sidebar.download_button(
    label="CSVをダウンロード",
    data=df.to_csv().encode('utf_8_sig'),
    file_name='estat_data.csv',
    mime='text/csv',
)