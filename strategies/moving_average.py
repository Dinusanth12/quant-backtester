def generate_signals(data, short_window=50, long_window=200):
    data['SMA50'] = data['Close'].rolling(window=short_window).mean()
    data['SMA200'] = data['Close'].rolling(window=long_window).mean()
    data['Signal'] = 0
    data.loc[data['SMA50'] > data['SMA200'], 'Signal'] = 1
    data.loc[data['SMA50'] < data['SMA200'], 'Signal'] = -1
    return data
