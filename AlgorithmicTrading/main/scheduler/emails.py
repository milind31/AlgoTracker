import math
import yfinance as yf
import backtrader as bt
import pandas as pd
from datetime import datetime, timedelta
from django.core.mail import send_mail

def send_email(email, ticker, strategy):
    stock_data = yf.Ticker(ticker)
    hist = stock_data.history(period="MAX")

    sell_dates = []
    order_dates = []
    order_limit_expiration_dates = []
    order_limit_prices = []
    
    #define strategies
    class ATR(bt.Strategy):
        params = (('n', 50), ('order_percentage', 1))
        
        def __init__(self):
            self.n_day_high = bt.ind.Highest(self.data.high, period=65)
            self.atr = bt.indicators.ATR(self.datas[0]) * 2
            
        def next(self):
            if self.position.size == 0:
                if self.data.close[0] > self.n_day_high[-1]:
                    amount_to_invest = (self.params.order_percentage * self.broker.cash)
                    self.size = math.floor(amount_to_invest / self.data.close) #order size
                    buy_price = self.data.low[0] - self.atr[0]
                    self.buy_order = self.buy(size=self.size, exectype=bt.Order.Limit, #place buy order
                            price=buy_price,
                            valid=self.datetime.date(ago=0) + timedelta(days=10))
                    order_dates.append(self.datetime.date(ago=0).strftime("%B %d, %Y"))
                    order_limit_expiration_dates.append((self.datetime.date(ago=0) + timedelta(days=10)).strftime("%B %d, %Y"))
                    order_limit_prices.append(buy_price)

            if self.position.size > 0:   
                sell = True
                for i in range(1,50):
                    neg_i = i * -1
                    if self.data.close[0] < self.data.close[neg_i]:
                        sell = False
                if sell == True:
                    self.close()
                    sell_dates.append(self.datetime.date(ago=0).strftime("%B %d, %Y"))
    
    class GoldenCross(bt.Strategy):
        params = (('fast', 50), ('slow', 200), ('order_percentage', 1), ('ticker', 'VOO'))

        def __init__(self):
            self.fast_moving_average = bt.indicators.SMA(self.data.close,
                                                        period = self.params.fast,
                                                        plotname = 'SMA {}'.format(self.params.fast))
            self.slow_moving_average = bt.indicators.SMA(self.data.close,
                                                        period = self.params.slow,
                                                        plotname = 'SMA {}'.format(self.params.slow))
            self.crossover = bt.indicators.CrossOver(self.fast_moving_average, self.slow_moving_average)
        
        def next(self):
            if self.position.size == 0:
                if self.crossover > 0:
                    amount_to_invest = (self.params.order_percentage * self.broker.cash)
                    self.size = math.floor(amount_to_invest / self.data.close)
                    self.buy(size=self.size)
                    order_dates.append(self.datetime.date(ago=0).strftime("%B %d, %Y"))
            
            if self.position.size > 0:
                if self.crossover < 0:
                    self.close()
                    sell_dates.append(self.datetime.date(ago=0).strftime("%B %d, %Y"))


    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(10000)
    feed = bt.feeds.PandasData(dataname=hist)
    cerebro.adddata(feed)

    if strategy == "ATR":
        cerebro.addstrategy(ATR)
    elif strategy == "GC":
        cerebro.addstrategy(GoldenCross)
    cerebro.run()

    yesterday = (datetime.today() - timedelta(days = 1)).strftime("%B %d, %Y") #figure out yesterdays date
    
    send_email = False #assume by default that we do not want to send an email

    if yesterday == sell_dates[-1]:
        send_email = True
        email_text = "EXECUTE SELL OF {}".format(ticker)
    elif yesterday == order_dates[-1]:
        send_email = True
        if strategy == "ATR":
            email_text = "EXECUTE BUY LIMIT FOR {} ENDING ON {} TO BUY AT ${}".format(ticker, order_limit_expiration_dates[-1], round(order_limit_prices[-1], 2))
            email_text += "\nCANCEL ANY PENDING BUY LIMITS"
        elif strategy == "GC":
            email_text = "GOLDEN CROSS SAYS EXECUTE BUY OF {}".format(ticker)
    
    if send_email == True:
        send_mail('EMAIL', email_text, 'noplif@gmail.com', [email], fail_silently=False)