# 从Binance币安在线api下载1分钟k线，进行回测
import requests
import backtrader as bt
import backtrader.analyzers as btanalyzers
import json
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

df = pd.read_csv("BTCUSDT_d.csv")
print(df.head())
print('k线数量', len(df))
print(df[1])
#df['datetime'] = pd.to_datetime(df['datetime'])#处理保存的时间 转换为时间格式
#df.set_index('datetime', inplace=True)