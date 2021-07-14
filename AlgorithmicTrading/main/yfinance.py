import yfinance as yf

#check if ticker is valid
def is_valid_ticker(ticker):
    stock = yf.Ticker(ticker)
    try:
        if stock.info:
            return True
    except:
        return False