from __future__ import(absolute_import, division, print_function, unicode_literals)
from datetime import datetime, timedelta
import backtrader as bt
from backtrader import cerebro
import time

class TestStrategy(bt.Strategy):
    def next(self):
        print('*' * 5, 'NEXT:', bt.num2date(self.data.datetime[0]), self.data._name, self.data.open[0], self.data.high[0],
              self.data.low[0], self.data.close[0], self.data.volume[0],
              bt.TimeFrame.getname(self.data._timeframe), len(self.data))
              
if __name__ == '__main__':
    cerebro = bt.Cerebro()

    hist_start_date = datetime.utcnow() - timedelta(minutes=10)
    data_min = bt.feeds.CCXT(exchange='bitmex', symbol="BTC/USD", name="btc_usd_min", fromdate=hist_start_date,
                             timeframe=bt.TimeFrame.Minutes)
    cerebro.adddata(data_min)
    cerebro.addstrategy(TestStrategy)
    cerebro.run()
