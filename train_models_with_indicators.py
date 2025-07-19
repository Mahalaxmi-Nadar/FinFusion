import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

# Load dataset
df = pd.read_csv("labeled_dataset_with_indicators.csv")

# Features to use
features = [
    "BTC_Boll_lower", "BTC_Boll_upper", "BTC_Change",
    "BTC_MACD", "BTC_MACD_signal", "BTC_RSI", "BTC_EMA_20", "BTC_Volume"
]

labels = ["Recommendation", "Term_Suggested", "Risk_Level"]
os.makedirs("models", exist_ok=True)

for label in labels:
    print(f"\n🎯 Training model for: {label}")
    
    # Encode label
    encoder = LabelEncoder()
    df[label] = encoder.fit_transform(df[label])
    label_mapping = dict(zip(encoder.transform(encoder.classes_), encoder.classes_))
    print("📚 Label Mapping:", label_mapping)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(df[features], df[label], test_size=0.2, random_state=42)

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print("📊 Classification Report:")
    print(classification_report(y_test, y_pred))

    # Save model and label encoder
    joblib.dump(model, f"models/{label}_model.pkl")
    joblib.dump(encoder, f"models/{label}_encoder.pkl")

print("\n✅ All models trained and saved in the 'models/' folder.")
