import math
import yfinance as yf
import plotly
import plotly.express as px
import plotly.graph_objs as go
import backtrader as bt
import pandas as pd
from datetime import datetime, timedelta

def make_plots(sell_dates, buy_dates, cash, ticker, hist):
    hist['Date'] = hist.index #create date column from dataframe index
    sell_prices = [hist['Close'][date] for date in sell_dates]
    buy_prices = [hist['Close'][date] for date in buy_dates]
    pct_changes = []
    for i in range(len(sell_prices)):
        net_gain_or_loss = sell_prices[i] - buy_prices[i]
        pct_changes.append((net_gain_or_loss/buy_prices[i])*100)

    buy_sell_fig = px.line(hist, x="Date", y="Close", title='Historical Buy/Sell Graph for {}'.format(ticker))
    buy_sell_fig.add_trace(
        go.Scatter(
        x=sell_dates,
        y=sell_prices,
        mode='markers',
        marker=dict
        (
        color='Red',
        size=10
        ),
        name='Sell')
    )
    buy_sell_fig.add_trace(
        go.Scatter(
        x=buy_dates,
        y=buy_prices,
        mode='markers',
        marker=dict
        (
        color='mediumspringgreen',
        size=10
        ),
        name='Buy')
    )
    
    outcomes = ["Gain" if pct_change > 0 else "Loss" for pct_change in pct_changes]
    df = pd.DataFrame({'a':cash, 'sell_dates':sell_dates, 'pct_changes':pct_changes, 'outcomes':outcomes})
    gain_loss_fig = px.scatter(data_frame= df,x='sell_dates', y='pct_changes',
                               color='outcomes',
                               title="Percent Gain/Loss for Trades",
                               labels={
                               "sell_dates": "Date",
                               "pct_changes": "Percent Gain/Loss",
                               "outcomes": "",
                               "a": "Total Cash"
                               },
                               size_max=10,
                               size=[1 for i in sell_dates],
                               hover_data="a"
                               )
    
    total_cash_fig = px.line(data_frame= df,x='sell_dates', y='a',
                        title="Total Cash After Each Sell ($10,000 Initial Investment)",
                        labels={
                            "sell_dates": "Date",
                            "a": "Cash",
                        }
                        )

    shares_bought = math.floor(10000 / hist['Close'][0])
    leftover_cash = 10000 -  (shares_bought * hist['Close'][0])
    total_cash_buy_hold_fig = px.line(x=hist['Date'], y=shares_bought * hist['Close'] + leftover_cash,
                                      title="Total Cash with Buy Hold Strategy ($10,000 Initial Investment)",
                                      labels={
                                          'x':"Date",
                                          'y':"Total Cash"
                                      }
                                      )

    buy_sell_graph = plotly.offline.plot(buy_sell_fig, auto_open = False, output_type="div")
    gain_loss_graph = plotly.offline.plot(gain_loss_fig, auto_open = False, output_type="div")
    total_cash_graph = plotly.offline.plot(total_cash_fig, auto_open = False, output_type="div")
    total_cash_buy_hold_graph = plotly.offline.plot(total_cash_buy_hold_fig, auto_open = False, output_type="div")

    return buy_sell_graph, gain_loss_graph, total_cash_graph, total_cash_buy_hold_graph


def get_plots(ticker, strategy):
    stock_data = yf.Ticker(ticker)
    hist = stock_data.history(period="MAX")

    sell_dates = []
    buy_dates = []
    cash = []
    
    #define strategies
    class ATR(bt.Strategy):
        params = (('n', 50), ('order_percentage', 1))
        
        def log(self, txt, order_type, dt=None):
            dt = dt or self.datas[0].datetime.date(0)
            if order_type == 'Buy':
                buy_dates.append(dt.isoformat())
            elif order_type == 'Sell':
                sell_dates.append(dt.isoformat())
                cash.append(self.broker.cash)
        
        def __init__(self):
            self.n_day_high = bt.ind.Highest(self.data.high, period=65)
            self.atr = bt.indicators.ATR(self.datas[0]) * 2
            
        def notify_order(self, order):
            if order.status in [order.Submitted, order.Accepted]:
                return
            
            if order.status in [order.Completed]:
                if order.isbuy():
                    self.log('BUY EXECUTED {}'.format(order.executed.price), 'Buy')
                elif order.issell():
                    self.log('SELL EXECUTED {}'.format(order.executed.price), 'Sell')
                self.bar_executed = len(self)

            self.order = None
        
        def next(self):
            if self.position.size == 0:
                if self.data.close[0] > self.n_day_high[-1]:
                    amount_to_invest = (self.params.order_percentage * self.broker.cash)
                    self.size = math.floor(amount_to_invest / self.data.close) #order size
                    buy_price = self.data.low[0] - self.atr[0]
                    self.buy_order = self.buy(size=self.size, exectype=bt.Order.Limit, #place buy order
                            price=buy_price,
                            valid=self.datetime.date(ago=0) + timedelta(days=10))

            if self.position.size > 0:   
                sell = True
                for i in range(1,50):
                    neg_i = i * -1
                    if self.data.close[0] < self.data.close[neg_i]:
                        sell = False
                if sell == True:
                    self.close()

    class GoldenCross(bt.Strategy):
        params = (('fast', 50), ('slow', 200), ('order_percentage', 1), ('ticker', 'VOO'))
        
        def log(self, txt, order_type, dt=None):
            dt = dt or self.datas[0].datetime.date(0)
            if order_type == 'Buy':
                buy_dates.append(dt.isoformat())
            elif order_type == 'Sell':
                sell_dates.append(dt.isoformat())
                cash.append(self.broker.cash)

        def __init__(self):
            self.fast_moving_average = bt.indicators.SMA(self.data.close,
                                                        period = self.params.fast,
                                                        plotname = 'SMA {}'.format(self.params.fast))
            self.slow_moving_average = bt.indicators.SMA(self.data.close,
                                                        period = self.params.slow,
                                                        plotname = 'SMA {}'.format(self.params.slow))
            self.crossover = bt.indicators.CrossOver(self.fast_moving_average, self.slow_moving_average)
        
        def notify_order(self, order):
            if order.status in [order.Submitted, order.Accepted]:
                return
            
            if order.status in [order.Completed]:
                if order.isbuy():
                    self.log('BUY EXECUTED {}'.format(order.executed.price), 'Buy')
                elif order.issell():
                    self.log('SELL EXECUTED {}'.format(order.executed.price), 'Sell')
                self.bar_executed = len(self)

            self.order = None
        
        def next(self):
            if self.position.size == 0:
                if self.crossover > 0:
                    amount_to_invest = (self.params.order_percentage * self.broker.cash)
                    self.size = math.floor(amount_to_invest / self.data.close)
                    
                    print("BUY {} SHARES OF {} AT {} on {}".format(self.size, self.params.ticker, round(self.data.close[0],2), self.datetime.date(ago=0)))
                    
                    self.buy(size=self.size)
            
            if self.position.size > 0:
                if self.crossover < 0:
                    print("SELL {} SHARES OF {} AT {} on {}".format(self.size, self.params.ticker, round(self.data.close[0],2), self.datetime.date(ago=0)))
                    self.close()

    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(10000)
    feed = bt.feeds.PandasData(dataname=hist)
    cerebro.adddata(feed)
    if strategy == "ATR":
        cerebro.addstrategy(ATR)
    elif strategy == "GC":
        cerebro.addstrategy(GoldenCross)
    cerebro.run()

    return make_plots(sell_dates, buy_dates, cash, ticker, hist)