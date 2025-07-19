import pandas as pd
import pandas_ta as ta
import warnings
warnings.filterwarnings('ignore')

# Load your labeled dataset
df = pd.read_csv("labeled_dataset.csv")

if 'BTC' not in df.columns:
    raise ValueError("BTC column is missing!")

df["BTC_Change"] = df["BTC"].pct_change() * 100
df["BTC_RSI"] = df.ta.rsi(close='BTC')

macd = df.ta.macd(close='BTC')
df = pd.concat([df, macd], axis=1)

bb = df.ta.bbands(close='BTC')
# Rename BBL and BBU to standard names
bb = bb.rename(columns={
    "BBL_20_2.0": "BTC_Boll_lower",
    "BBU_20_2.0": "BTC_Boll_upper"
})
df = pd.concat([df, bb], axis=1)

df["BTC_EMA_20"] = df.ta.ema(close='BTC', length=20)
df.dropna(inplace=True)

df.to_csv("labeled_dataset_with_indicators.csv", index=False)
print("✅ Indicators added and saved to labeled_dataset_with_indicators.csv")
