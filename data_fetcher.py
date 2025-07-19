# data_fetcher.py
import yfinance as yf
import pandas as pd
import pandas_ta as ta

def fetch_indicators():
    print("📥 Downloading BTC-USD data...")

    try:
        df = yf.download("BTC-USD", period="90d", interval="1d", auto_adjust=True)
        if df is None or df.empty:
            print("❌ Dataframe is empty.")
            return None

        print("✅ Data downloaded. Calculating indicators...")

        # Compute indicators
        bb = ta.bbands(df['Close'], length=20)
        macd = ta.macd(df['Close'])
        rsi = ta.rsi(df['Close'], length=14)
        ema = ta.ema(df['Close'], length=20)

        # Combine all into one dataframe
        if bb is not None:
            df = pd.concat([df, bb], axis=1)
        if macd is not None:
            df = pd.concat([df, macd], axis=1)
        if rsi is not None:
            df['RSI'] = rsi
        if ema is not None:
            df['EMA_20'] = ema

        # Drop rows with any NaNs (usually first 26-30 days)
        df.dropna(inplace=True)

        if df.empty:
            print("❌ All rows dropped after removing NaNs.")
            return None

        # Extract latest valid row
        last = df.iloc[-1]

        indicators = {
            "BTC_Boll_lower": round(last.get("BBL_20_2.0", 0.0), 2),
            "BTC_Boll_upper": round(last.get("BBU_20_2.0", 0.0), 2),
            "BTC_Change": round(df["Close"].pct_change().dropna().iloc[-1] * 100, 2),
            "BTC_MACD": round(last.get("MACD_12_26_9", 0.0), 2),
            "BTC_MACD_signal": round(last.get("MACDs_12_26_9", 0.0), 2),
            "BTC_RSI": round(last.get("RSI", 0.0), 2),
            "BTC_EMA_20": round(last.get("EMA_20", 0.0), 2),
            "BTC_Volume": round(last.get("Volume", 0.0), 2)
        }

        print("✅ Final Indicators:", indicators)
        return indicators

    except Exception as e:
        print("❌ Exception:", e)
        return None
