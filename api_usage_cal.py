import glob
import pandas as pd

yen_rate = 150

def display_selected_columns_and_total(data, columns=['context_tokens', 'context_price', 'generated_tokens', 'generated_price', 'total_price']):
    # 結果を表示する
    total = data['context_price'].sum() + data['generated_price'].sum()
    print(data[columns])
    print("total_price: ", total)

def rename_columns_and_fill_nan(df):
    # カラム名を変更する
    df = df.rename(columns={'n_context_tokens_total': 'context_tokens'})
    df = df.rename(columns={'n_generated_tokens_total': 'generated_tokens'})

    # 'api_key_name'列の欠損値を'unknown'で埋める
    df['api_key_name'] = df['api_key_name'].fillna('unknown')
    return df

def fetch_model_pricing_data(df_pricing, model):
    # modelの前方20文字でdf_pricingから適切な行を検索する
    pricing_rows = df_pricing[df_pricing['model'].str.startswith(model[:20])]

    if pricing_rows.empty:
        print("Warning: No pricing data found for model", model)
        pricing_row = pd.Series({'model': "unknown", 'n_context_tokens_total_pricing': 1, 'n_generated_tokens_total_pricing': 1,'per_token': 1})
    else:
        pricing_row = pricing_rows.iloc[0]

    return pricing_row

def calculate_and_append_prices(df, df_pricing):
    # 'api_keyname'と'user', 'model'情報ごとにデータをグループ化し、'context_tokens'と'generated_tokens'をそれぞれまとめる
    grouped = df.groupby(['user', 'api_key_name', 'model']).sum()

    # 空のリストを作成する
    n_context_tokens_total_prices = []
    n_generated_tokens_total_prices = []

    # groupedの各行に対してループを行う
    for i, row in grouped.iterrows():
        pricing_row = fetch_model_pricing_data(df_pricing, i[2])

        # 料金を計算する
        n_context_tokens_total_price = row['context_tokens'] * pricing_row.iloc[1] / pricing_row.iloc[3] * yen_rate
        n_context_tokens_total_prices.append(n_context_tokens_total_price)

        n_generated_tokens_total_price = row['generated_tokens'] * pricing_row.iloc[2] / pricing_row.iloc[3] * yen_rate
        n_generated_tokens_total_prices.append(n_generated_tokens_total_price)

    # groupedに新しい列として料金を追加する
    grouped['context_price'] = n_context_tokens_total_prices
    grouped['generated_price'] = n_generated_tokens_total_prices
    grouped['total_price'] = grouped['context_price'] + grouped['generated_price']

    # 結果を表示する
    display_selected_columns_and_total(grouped)

# CSVファイルを読み込む
df_pricing = pd.read_csv('pricing_data.csv')
# 'activity'で始まり'.csv'で終わるファイル名を取得する
csv_files = glob.glob('activity*.csv')

# 各ファイルを読み込む
for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    df = rename_columns_and_fill_nan(df)
    # ここにデータフレームを処理するコードを書く
    print("Total price for", csv_file)
    calculate_and_append_prices(df, df_pricing)
