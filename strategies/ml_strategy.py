
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def generate_features(data):
    data['Return'] = data['Close'].pct_change()
    data['SMA_10'] = data['Close'].rolling(window=10).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['RSI'] = compute_rsi(data['Close'], window=14)
    data['Momentum'] = data['Close'] - data['Close'].shift(10)
    data['Volatility'] = data['Return'].rolling(window=10).std()
    data = data.dropna()
    return data

def compute_rsi(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def generate_signals(data):
    data = generate_features(data)

    # Labels: 1 for buy, -1 for sell based on forward returns
    data['Target'] = np.where(data['Return'].shift(-1) > 0, 1, -1)

    features = ['SMA_10', 'SMA_50', 'RSI', 'Momentum', 'Volatility']
    X = data[features]
    y = data['Target']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, shuffle=False
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    data['Signal'] = model.predict(X_scaled)
    return data
