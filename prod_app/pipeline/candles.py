import requests

base_url = "https://api-pub.bitfinex.com/v2/candles/trade:%s:t%s/%s"

def get_current_candle(symbol, timeframe):
    url = base_url % (timeframe, symbol.upper(), "last")
    candles_data = requests.get(url).json()
    candle = {
        'timestamp': candles_data[0],
        'open': candles_data[1],
        'close': candles_data[2],
        'high': candles_data[3],
        'low': candles_data[4],
    }
    return candle
