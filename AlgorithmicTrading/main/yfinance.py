import yfinance as yf

def is_valid_ticker(ticker):
    stock = yf.Ticker(ticker)
    try:
        if stock.info:
            return True
    except:
        return False