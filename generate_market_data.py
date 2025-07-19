import pandas as pd

# Load dataset
df = pd.read_csv("Dataset.csv")

# Fill missing values if any
df.ffill(inplace=True)

# Create % change columns
df['BTC_Change'] = df['BTC'].pct_change() * 100
df['Stock_Avg'] = df[['NYSE', 'NASDAQ', 'LSE']].mean(axis=1)
df['Stock_Change'] = df['Stock_Avg'].pct_change() * 100

# Logic for Recommendation
def recommend(row):
    if row['BTC_Change'] > 2 or row['Stock_Change'] > 1.5:
        return 'Buy'
    elif row['BTC_Change'] < -2 or row['Stock_Change'] < -1.5:
        return 'Sell'
    else:
        return 'Hold'

# Logic for Term Suggestion
def suggest_term(row):
    if abs(row['BTC_Change']) > 3 or abs(row['Stock_Change']) > 2:
        return 'Short-term'
    else:
        return 'Long-term'

# Logic for Risk Level
def risk_level(row):
    volatility = max(abs(row['BTC_Change']), abs(row['Stock_Change']))
    if volatility > 5:
        return 'High'
    elif volatility > 2:
        return 'Medium'
    else:
        return 'Low'

# Add new columns
df['Recommendation'] = df.apply(recommend, axis=1)
df['Term_Suggested'] = df.apply(suggest_term, axis=1)
df['Risk_Level'] = df.apply(risk_level, axis=1)

# Drop first row due to NaN in pct_change
df.dropna(inplace=True)

# Save enriched dataset
df.to_csv("labeled_dataset.csv", index=False)
print("✅ Labels added. Dataset ready.")
