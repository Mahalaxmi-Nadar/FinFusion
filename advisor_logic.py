import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import numpy as np

# Sample dataset
data = pd.DataFrame({
    'amount': [1000, 5000, 10000, 15000, 20000, 3000, 7000, 8000],
    'risk': ['low', 'medium', 'high', 'medium', 'low', 'high', 'low', 'medium'],
    'recommendation': ['FD/Gold', 'Index Funds', 'Crypto', 'Mutual Funds', 'Gov Bonds', 'Altcoins', 'REITs', 'Balanced Fund'],
    'term': ['Long-term', 'Long-term', 'Short-term', 'Long-term', 'Long-term', 'Short-term', 'Long-term', 'Long-term']
})

# Map risk to numeric
data['risk_num'] = data['risk'].map({'low': 0, 'medium': 1, 'high': 2})

X = data[['amount', 'risk_num']]
y = data[['recommendation', 'term']]

# Train models for both recommendation and term
rec_model = DecisionTreeClassifier()
rec_model.fit(X, y['recommendation'])

term_model = DecisionTreeClassifier()
term_model.fit(X, y['term'])

# Enhanced logic
def get_enhanced_recommendation(amount: float, risk: str) -> dict:
    risk_map = {'low': 0, 'medium': 1, 'high': 2}
    if risk not in risk_map:
        return {"error": "Invalid risk level. Choose from low, medium, or high."}

    risk_num = risk_map[risk]
    input_data = [[amount, risk_num]]

    recommendation = rec_model.predict(input_data)[0]
    term = term_model.predict(input_data)[0]

    # Simulated confidence score
    distances = np.abs(data['amount'] - amount)
    confidence = max(60, 100 - int(distances.mean() / 200))

    # Determine asset risk (mock logic based on type)
    if recommendation in ['FD/Gold', 'Gov Bonds']:
        asset_risk = 'Low'
    elif recommendation in ['Mutual Funds', 'Index Funds', 'REITs']:
        asset_risk = 'Moderate'
    else:
        asset_risk = 'High'

    # Risk explanation logic
    if asset_risk == 'Low':
        explanation = (
            f"You selected {risk} risk. {recommendation} is considered low risk due to its stable nature and guaranteed returns. "
            f"Suitable for preserving capital even with smaller amounts like ₹{amount}."
        )
    elif asset_risk == 'Moderate':
        explanation = (
            f"You selected {risk} risk. {recommendation} carries moderate risk and usually gives decent long-term returns. "
            f"Your investment of ₹{amount} aligns well with this asset."
        )
    else:
        explanation = (
            f"You selected {risk} risk. {recommendation} is highly volatile and suitable for users looking for aggressive growth. "
            f"Since you're investing ₹{amount}, make sure you're ready for possible ups and downs."
        )

    return {
        "recommendation": recommendation,
        "term": term,
        "risk_level": asset_risk,
        "risk_explanation": explanation,
        "confidence": f"{confidence}%"
    }
