import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

# Load enriched dataset
df = pd.read_csv("labeled_dataset.csv")

# Define input features
features = ['BTC', 'NYSE', 'NASDAQ', 'LSE', 'BTC_Volume', 'NYSE_Volume', 'NASDAQ_Volume', 'LSE_Volume']
X = df[features]

# Create models folder
os.makedirs("models", exist_ok=True)

# Loop through each label to train individual models
labels = ['Recommendation', 'Term_Suggested', 'Risk_Level']

for label in labels:
    y = df[label]

    # Encode labels
    y_encoded = y.astype('category').cat.codes
    label_mapping = dict(enumerate(y.astype('category').cat.categories))

    print(f"\n🎯 Training model for: {label}")
    print("Label mapping:", label_mapping)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    # Train Random Forest model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print("\n📊 Evaluation Report:")
    print(classification_report(y_test, y_pred, target_names=label_mapping.values()))

    # Save model & label map
    joblib.dump(model, f"models/{label}_model.pkl")
    joblib.dump(label_mapping, f"models/{label}_labels.pkl")

print("\n✅ All models trained and saved in 'models/' folder.")
