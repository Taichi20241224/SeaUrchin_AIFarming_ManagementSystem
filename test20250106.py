import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt
import time

# Google Sheets API 認証設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_path = '/Volumes/The 3rd Hippocampus -5Tb-/Research/Research_Project_Plan/SeaUrchin_AIFarming_ManagementSystem/scripts/credentials.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(credentials)

# スプレッドシートのURL
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1ItEKoQ2vqvvO7biQ_vsQiLNPEdeAt0ttor52_klgl_g/edit#gid=0'
worksheet = client.open_by_url(spreadsheet_url).get_worksheet(0)

# グラフ描画関数
def plot_individual_columns(df, columns_to_plot, latest_n=30):
    """列ごとに独立してプロットを作成"""
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))  # 2行×4列のグラフ構成
    axes = axes.flatten()

    for i, column in enumerate(columns_to_plot):
        ax = axes[i]

        # 数値データの変換
        df[column] = pd.to_numeric(df[column], errors='coerce')

        # 最新データ取得（欠損を除外）
        column_data = df[['Date', column]].dropna().tail(latest_n)

        if column_data.empty:
            ax.text(0.5, 0.5, f"No data for {column}", fontsize=12, ha='center')
            ax.set_title(f'{column} Over Time', fontsize=10)
            continue

        # プロット作成
        ax.plot(column_data['Date'], column_data[column], marker='o', linestyle='-', label=column)
        ax.set_xlabel('Date', fontsize=8)
        ax.set_ylabel(column, fontsize=8)
        ax.set_title(f'{column} Over Time (Last {latest_n})', fontsize=10)
        ax.legend(fontsize=8)
        ax.grid()

        # x軸を月日（%m-%d形式）で表示
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))

    # 残りの空プロットを削除
    for j in range(len(columns_to_plot), len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.pause(1)  # 更新の間を空ける
    plt.show(block=False)

# 実行
columns_to_plot = ['Temp.', 'pH', 'Sal.', 'DO', 'NH3-NH4+', 'NO2-', 'NO3-']

while True:
    try:
        # データ取得
        all_data = worksheet.get_all_values()
        data = all_data[2:]  # データ部分（3行目以降）
        headers = all_data[0]  # ヘッダー
        df = pd.DataFrame(data, columns=headers)
        df.columns = df.columns.str.strip().str.replace('\n', '', regex=True)

        # Date列の変換
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d', errors='coerce')
        df = df.dropna(subset=['Date'])  # 無効な日付を削除

        # 最新データを取得
        plot_individual_columns(df, columns_to_plot, latest_n=30)

        # グラフを閉じて次の更新
        plt.pause(1)  # 更新間隔
        plt.close('all')  # グラフを閉じる
    except Exception as e:
        print(f"エラー: {e}")

    time.sleep(30)  # 30秒ごとに更新