import pandas as pd

yen_rate = 150

# CSVファイルを読み込む
df = pd.read_csv('activity-2024-03-01-2024-04-01.csv')
df_pricing = pd.read_csv('pricing_data.csv')

# カラム名を変更する
df = df.rename(columns={'n_context_tokens_total': 'context_tokens'})
df = df.rename(columns={'n_generated_tokens_total': 'generated_tokens'})

# 'api_key_name'列の欠損値を'unknown'で埋める
df['api_key_name'] = df['api_key_name'].fillna('unknown')

# 'api_keyname'と'user', 'model'情報ごとにデータをグループ化し、'context_tokens'と'generated_tokens'をそれぞれまとめる
grouped = df.groupby(['user', 'api_key_name', 'model']).sum()

# 空のリストを作成する
n_context_tokens_total_prices = []
n_generated_tokens_total_prices = []

# groupedの各行に対してループを行う
for i, row in grouped.iterrows():
    # i[2]の前方20文字でdf_pricingから適切な行を検索する
    pricing_rows = df_pricing[df_pricing['model'].str.startswith(i[2][:20])]

    if pricing_rows.empty:
        print("Warning: No pricing data found for model", i[2])
        pricing_row = pd.Series({'model': "unknown", 'n_context_tokens_total_pricing': 1, 'n_generated_tokens_total_pricing': 1,'per_token': 1})
    else:
        pricing_row = pricing_rows.iloc[0]

    # 料金を計算する
    n_context_tokens_total_price = row['context_tokens'] * pricing_row.iloc[1] / pricing_row.iloc[3] * yen_rate
    n_context_tokens_total_prices.append(n_context_tokens_total_price)

    n_generated_tokens_total_price = row['generated_tokens'] * pricing_row.iloc[2] / pricing_row.iloc[3] * yen_rate
    n_generated_tokens_total_prices.append(n_generated_tokens_total_price)

# groupedに新しい列として料金を追加する
grouped['context_price'] = n_context_tokens_total_prices
grouped['generated_price'] = n_generated_tokens_total_prices
grouped['total_price'] = grouped['context_price'] + grouped['generated_price']

# 全体でかかった金額を計算する
total_price = grouped['context_price'].sum() + grouped['generated_price'].sum()

# 結果を表示する
print(grouped[['context_tokens', 'context_price', 'generated_tokens', 'generated_price', 'total_price']])
print("total_price: ", total_price)