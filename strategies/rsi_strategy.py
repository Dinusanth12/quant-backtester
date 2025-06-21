def generate_signals(data, rsi_period=14, lower=30, upper=70):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    data['Signal'] = 0
    data.loc[data['RSI'] < lower, 'Signal'] = 1
    data.loc[data['RSI'] > upper, 'Signal'] = -1
    return data
