# STEP F1: Download 2 Years of BTC-USD Data with Indicators
import yfinance as yf
import pandas as pd
import pandas_ta as ta

print("\U0001F4E5 Downloading 730 days of BTC-USD data...")
df = yf.download("BTC-USD", period="730d", interval="1d", auto_adjust=False)

# STEP F2: Clean column names

df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
df.columns = [str(col).strip().title() for col in df.columns]
df.dropna(subset=["Adj Close", "Volume"], inplace=True)

print("\n🔎 Last 5 rows of Adj Close and Volume:")
print(df[["Adj Close", "Volume"]].tail())
# STEP F3: Ensure enough rows
if len(df) < 25:
    raise ValueError("❌ Not enough data to compute technical indicators.")

# STEP F4: Add technical indicators
df["BTC_Change"] = df["Adj Close"].pct_change() * 100

bb = ta.bbands(close=df["Adj Close"], length=20)
if bb is None or bb.empty:
    raise ValueError("❌ Bollinger Bands data not available.")
df["BTC_Boll_lower"] = bb["BBL_20_2.0"]
df["BTC_Boll_upper"] = bb["BBU_20_2.0"]

macd = ta.macd(close=df["Adj Close"])
if macd is None or macd.empty:
    raise ValueError("❌ MACD data not available.")
df["BTC_MACD"] = macd["MACD_12_26_9"]
df["BTC_MACD_signal"] = macd["MACDs_12_26_9"]

rsi = ta.rsi(close=df["Adj Close"], length=14)
if rsi is None or rsi.empty:
    raise ValueError("❌ RSI data not available.")
df["BTC_RSI"] = rsi

ema = ta.ema(close=df["Adj Close"], length=20)
if ema is None or ema.empty:
    raise ValueError("❌ EMA data not available.")
df["BTC_EMA_20"] = ema

df["BTC_Volume"] = df["Volume"]
df = df.dropna().copy()

# STEP F5: Generate Intelligent Labels

df["Recommendation"] = df.apply(
    lambda row: "Invest" if row["BTC_MACD"] > row["BTC_MACD_signal"] and row["BTC_Change"] > 0
    else "Hold" if abs(row["BTC_Change"]) < 0.5
    else "Avoid",
    axis=1
)

df["Term_Suggested"] = df["BTC_EMA_20"].rolling(window=3).mean().shift(1).lt(df["BTC_EMA_20"]).map(
    {True: "Short-Term", False: "Long-Term"}
).fillna("Short-Term")

df["Risk_Level"] = df["BTC_RSI"].apply(
    lambda rsi: "High" if rsi > 70 else ("Low" if rsi < 30 else "Medium")
)

# STEP F6: Save
output_file = "labeled_dataset_with_indicators.csv"
df.to_csv(output_file, index=False)
print(f"\n✅ Dataset with intelligent labels saved successfully to {output_file}!")
