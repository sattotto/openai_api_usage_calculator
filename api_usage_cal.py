import pandas as pd

yen_rate = 150

# CSVファイルを読み込む
df = pd.read_csv('activity-2024-03-01-2024-04-01.csv')
df_pricing = pd.read_csv('pricing_data.csv')

# 'api_key_name'列の欠損値を'unknown'で埋める
df['api_key_name'] = df['api_key_name'].fillna('unknown')

# 'api_keyname'と'user', 'model'情報ごとにデータをグループ化し、'context_tokens'と'generated_tokens'をそれぞれまとめる
grouped = df.groupby(['user', 'api_key_name', 'model']).sum()

# 空のリストを作成する
n_context_tokens_total_prices = []
n_generated_tokens_total_prices = []

# groupedの各行に対してループを行う
for i, row in grouped.iterrows():
        # i[2]の前方10文字でdf_pricingから適切な行を検索する
    pricing_rows = df_pricing[df_pricing['model'].str.startswith(i[2][:10])]

    if pricing_rows.empty:
        pricing_row = pd.Series({'model': "unknown", 'n_context_tokens_total_pricing': 1, 'n_generated_tokens_total': 1,'per_token': 1})
    else:
        pricing_row = pricing_rows.iloc[0]

    # 料金を計算する
    n_context_tokens_total_price = row['n_context_tokens_total'] * pricing_row[1] / pricing_row[3] * yen_rate
    n_context_tokens_total_prices.append(n_context_tokens_total_price)

    n_generated_tokens_total_price = row['n_generated_tokens_total'] * pricing_row[2] / pricing_row[3] * yen_rate
    n_generated_tokens_total_prices.append(n_generated_tokens_total_price)

# groupedに新しい列として料金を追加する
grouped['n_context_tokens_total_price'] = n_context_tokens_total_prices
grouped['n_generated_tokens_total_price'] = n_generated_tokens_total_prices

# 結果を表示する


print(grouped[['n_context_tokens_total', 'n_context_tokens_total_price', 'n_generated_tokens_total', 'n_generated_tokens_total_price']])

# 全体でかかった金額を計算する
total_price = grouped['n_context_tokens_total_price'].sum() + grouped['n_generated_tokens_total_price'].sum()

# 結果を表示する
print("total_price: ", total_price)