import joblib
import pandas as pd

model = joblib.load("models/Recommendation_model.pkl")
labels = joblib.load("models/Recommendation_labels.pkl")

data = pd.DataFrame([{
    "BTC_Boll_lower": 100,
    "BTC_Boll_upper": 105,
    "BTC_Change": 1.2,
    "BTC_MACD": 0.4,
    "BTC_MACD_signal": 0.3,
    "BTC_RSI": 50,
    "BTC_EMA_20": 102,
    "BTC_Volume": 500000000
}])

prediction = model.predict(data)
print("Recommendation:", labels[prediction[0]])
