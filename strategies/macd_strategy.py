def generate_signals(data, fast=12, slow=26, signal=9):
    data['EMA_fast'] = data['Close'].ewm(span=fast, adjust=False).mean()
    data['EMA_slow'] = data['Close'].ewm(span=slow, adjust=False).mean()
    data['MACD'] = data['EMA_fast'] - data['EMA_slow']
    data['SignalLine'] = data['MACD'].ewm(span=signal, adjust=False).mean()

    data['Signal'] = 0
    data.loc[data['MACD'] > data['SignalLine'], 'Signal'] = 1
    data.loc[data['MACD'] < data['SignalLine'], 'Signal'] = -1
    return data
