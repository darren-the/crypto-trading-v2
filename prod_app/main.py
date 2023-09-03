from flask import Flask
from google.appengine.api.mail import SendMailToAdmins
from google.appengine.api import wrap_wsgi_app
from pipeline.candles import get_current_candle

app = Flask(__name__)
app.wsgi_app = wrap_wsgi_app(app.wsgi_app)

@app.route("/")
def hello_world():
    symbol = 'BTCUSD'
    timeframe = '1D'
    candle = get_current_candle(symbol, timeframe)
    SendMailToAdmins(
        sender="darren.the7@gmail.com",
        subject=f"{symbol} price: {candle['close']}",
        body=""
    )
    return "<p>Hello, World!</p>"
