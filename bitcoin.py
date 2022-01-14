# 从Binance币安在线api下载1分钟k线，进行回测
from csv import unix_dialect
from dataclasses import replace
import requests
import backtrader as bt
import backtrader.analyzers as btanalyzers
import json
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import math

class sizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            return math.floor(cash/data[1])
        else:
            return self.broker.getposition(data)

class MaCrossStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt)) 
    # 設定交易參數
    params = dict(
        ma_period_short=5,
        ma_period_long=10
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.ma_period_short)
        sma2 = bt.ind.SMA(period=self.p.ma_period_long)
        self.crossover = bt.ind.CrossOver(sma1, sma2)
        self.setsizer(sizer())

        #self.crossover = bt.ind.CrossOver(self.ma_fast, self.ma_slow)

        self.dataopen = self.datas[0].open

    def next(self):
        # 帳戶沒有部位
            # 5ma往上穿越20ma
        if self.crossover > 0:
            # 印出買賣日期與價位
            self.log('BUY ' + ', Price: ' + str(self.dataopen[0]))
            # 使用開盤價買入標的
            self.buy(price=self.dataopen[0])
        # 5ma往下穿越20ma
        elif self.crossover < 0:
            print(1)
            # 印出買賣日期與價位
            self.log('SELL ' + ', Price: ' + str(self.dataopen[0]))
            # 使用開盤價賣出標的
            self.close(price=self.dataopen[0])

    


df = pd.read_csv("BTCUSDT_d.csv")
#print(df.head())
print('k线数量', len(df))
#print(df['date'])
df['datetime'] = pd.to_datetime(df['date'])#处理保存的时间 转换为时间格式
df.set_index('datetime', inplace=True)
df.drop(['unix','date','symbol','Volume BTC','Volume USDT','tradecount'], axis=1,inplace=True)
print(df.head())


cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)#数据
cerebro.addstrategy(MaCrossStrategy)#策略
cerebro.broker.setcash(100000.0)#初始资金

#cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
# cerebro.addanalyzer(btanalyzers.SharpeRatio, timeframe=bt.TimeFrame.Minutes, _name="sharpe")
# cerebro.addanalyzer(btanalyzers.Transactions, _name="trans")

cerebro.run()
cerebro.plot()
# print('最终市值', cerebro.broker.getvalue())  # Ending balance
# print(back[0].analyzers.sharpe.get_analysis()["sharpe"])  # Sharpe
# print(len(back[0].analyzers.trans.get_analysis()))