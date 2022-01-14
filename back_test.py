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
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo


class TestStrategy(bt.Strategy):
    """
    继承并构建自己的策略
    """
    def log(self, txt, dt=None, doprint=False):
        "日志函数，用于统一输出日志格式"
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('{}, {}'.format(dt.isoformat(), txt))

    def __init__(self):
        # 初始化相关数据
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # 移动平均线初始化
        self.sma5 = bt.indicators.MovingAverageSimple(self.datas[0], period=5)
        self.sma20 = bt.indicators.MovingAverageSimple(self.datas[0], period=20)

    def notify_order(self, order):
        """
        订单状态处理
        Arguments:
            order {object} -- 订单状态
        """
        if order.status in [order.Submitted, order.Accepted]:
            # 如订单已被处理，则不用做任何事情
            return

        # 检查订单是否完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            self.bar_executed = len(self)

        # 订单因为缺少资金之类的原因被拒绝执行
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # 订单状态处理完成，设为空
        self.order = None

    def notify_trade(self, trade):
        """
        交易成果
        Arguments:
            trade {object} -- 交易状态
        """
        if not trade.isclosed:
            return

        # 显示交易的毛利率和净利润
        self.log('OPERATION PROFIT, GROSS {}, NET {}'.format(trade.pnl, trade.pnlcomm), doprint=True)

    def next(self):
        ''' 下一次执行 '''

        # 记录收盘价
        

        # 是否正在下单，如果是的话不能提交第二次订单
        if self.order:
            return

        # 是否已经买入
        if not self.position:
            self.log('Close, {}'.format(self.dataclose[0]), doprint=True)
            # 还没买，如果 MA5 > MA10 说明涨势，买入
            if self.sma5[0] > self.sma20[0]:
                self.order = self.buy()
        else:
            # 已经买了，如果 MA5 < MA10 ，说明跌势，卖出
            if self.sma5[0] < self.sma20[0]:
                self.order = self.sell()


df = pd.read_csv("BTCUSDT_d.csv")
#print(df.head())
print('k线数量', len(df))
#print(df['date'])
df['datetime'] = pd.to_datetime(df['date'])#处理保存的时间 转换为时间格式
df.set_index('datetime', inplace=True)
df.drop(['unix','date','symbol','Volume BTC','Volume USDT','tradecount'], axis=1,inplace=True)
print(df.head())

cerebro = bt.Cerebro()
init_cash = 1000000.0
fromdate = dt.datetime(2020, 3, 14)
todate = dt.datetime(2022, 1, 12)

#构建策略
strategy = cerebro.addstrategy(TestStrategy)

#每次买100股
cerebro.addsizer(bt.sizers.PercentSizer, percents=100)

# data = bt.feeds.GenericCSVData(
#         dataname='BTCUSDT_d.csv',
#         fromdate=fromdate,
#         todate=todate,
#         dtformat='%Y%m%d',
#         datetime=1,
#         open=2,
#         high=3,
#         low=4,
#         close=5,
#         volume=6
#     )

#data = bt.feeds.PandasData(dataname=df,fromdate=fromdate,todate=todate)
class pandasDataFeed(bt.feeds.PandasData):
    #lines = ('vwap')
    params = (
        ('fromdate', fromdate),
        ('todate', todate),
        ('dtformat', '%Y-%m-%d'),
        ('datetime', None),
        ('high', 'high'),
        ('low', 'low'),
        ('open', 'open'),
        ('close', 'close')
        #('volume', 'Volume')
        #('vwap', 'VWAP')
    )
data = pandasDataFeed(dataname=df)
cerebro.adddata(data)

cerebro.broker.setcash(init_cash)

print('启动资金: {}'.format(cerebro.broker.getvalue()))

cerebro.run()

print('策略结束时资金: {}'.format(cerebro.broker.getvalue()))

duration_year = (todate-fromdate).days/360

end_value = cerebro.broker.getvalue()
roi = pow(end_value/init_cash, 1/duration_year)-1
print('策略年华收益率: {}%'.format(roi*100))
b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
#cerebro.plot(b)