// static/script.js
async function autoFillIndicators() {
  const response = await fetch("/get-latest-indicators");
  const data = await response.json();
  for (let key in data) {
    const input = document.getElementById(key);
    if (input) input.value = data[key];
  }
}

async function submitForm() {
  const fields = [
    "BTC_Boll_lower", "BTC_Boll_upper", "BTC_Change",
    "BTC_MACD", "BTC_MACD_signal", "BTC_RSI",
    "BTC_EMA_20", "BTC_Volume"
  ];

  const inputData = {};
  for (let field of fields) {
    inputData[field] = parseFloat(document.getElementById(field).value);
  }

  const response = await fetch("/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(inputData),
  });

  const result = await response.json();
  document.getElementById("result").innerText = JSON.stringify(result, null, 2);
}
