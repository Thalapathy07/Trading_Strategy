import yfinance as yf
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
yf.pdr_override()

stock = input('Stock name is: ')
num_days = int(input('Number of days the analysis needs to be done(Please enter an integer): '))


start_date = (datetime.datetime.now() - datetime.timedelta(days = num_days)).strftime("%Y-%m-%d")
df = pdr.get_data_yahoo(stock, start = start_date)
df.dropna(how = 'any', inplace = True)


plt.figure(figsize=(15, 8))
plt.plot(df['Adj Close'], label = stock, linewidth = 0.5)
plt.title('Adjacent close price history')
plt.xlabel('Previous ' + str(num_days) + ' days')
plt.ylabel('Adj. close price (₹)')
plt.legend(loc = 'upper left')
plt.show()

SMA20 = pd.DataFrame()
SMA20['Price'] = df['Adj Close'].rolling(window = 20).mean()
SMA50 = pd.DataFrame()
SMA50['Price'] = df['Adj Close'].rolling(window = 50).mean()

Data = pd.DataFrame()
Data['Price'] = df['Adj Close']
Data['SMA20'] = SMA20['Price']
Data['SMA50'] = SMA50['Price']
Data['funds'] = 100000

def buy_sell_signal(data):
  buy_signal = []
  sell_signal = []
  open_position = []
  funds = [100000] * len(data)
  last_funds = 100000
  flag = 0  # flag = 0 means sell_flag and flag = 1 means buy_flag

  for i in range(len(data)):
    if data['SMA20'][i] > data['SMA50'][i]:
      if flag == 0:
        flag = 1
        buy_signal.append(data['Price'][i])
        last_pos = last_funds / data['Price'][i]
        funds[i] = last_funds
        open_position.append(last_pos)     # buy_quantity with 1 Lac Capital
        sell_signal.append(np.NaN)
      else:
        buy_signal.append(np.NaN)
        last_funds = data['Price'][i] * last_pos
        funds[i] = last_funds
        open_position.append(last_pos)
        sell_signal.append(np.NaN)
    elif data['SMA20'][i] < data['SMA50'][i]:
      if flag == 1:
        flag = 0
        buy_signal.append(np.NaN)
        last_funds = last_pos * data['Price'][i]
        funds[i] = last_funds
        open_position.append(0)
        sell_signal.append(data['Price'][i])
      else:
        buy_signal.append(np.NaN)
        funds[i] = last_funds
        open_position.append(0)
        sell_signal.append(np.NaN)
    else:
      buy_signal.append(np.NaN)
      open_position.append(0)
      sell_signal.append(np.NaN)
  return buy_signal, sell_signal, open_position, funds, flag


buy_sell = buy_sell_signal(Data)
#print(buy_sell)
Data['Buy_price'] = buy_sell[0]
Data['Sell_price'] = buy_sell[1]
Data['Open_pos'] = buy_sell[2]
Data['live_pos'] = Data['Open_pos'].multiply(Data['Price'])
Data['funds'] = buy_sell[3]

# Visualize Data and strategy to buy and sell NIFTY
plt.figure(figsize = (15, 8))
plt.plot(Data['Price'], label = str(stock), linewidth = 1)
plt.plot(Data['SMA20'], label = 'SMA20', linewidth = 0.5)
plt.plot(Data['SMA50'], label = 'SMA50', linewidth = 0.5)
plt.scatter(Data.index, Data['Buy_price'], label= 'Buy', marker = '^', color = 'g')
plt.scatter(Data.index, Data['Sell_price'], label= 'Sell', marker = 'v', color = 'r')
plt.title(str(stock) + ' Buy-Sell Signals')
plt.xlabel(num_days)
plt.ylabel('Close price (₹)')
plt.legend(loc = 'upper left')
plt.show()

# Visualize results / PnL
plt.figure(figsize = (15, 8))
plt.plot(Data['funds'], linewidth = 1.0)
plt.xticks(rotation=45)
plt.show()