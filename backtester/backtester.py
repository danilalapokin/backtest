import numpy as np
import pandas as pd
import time
from datetime import datetime
from tqdm import tqdm
import matplotlib.pyplot as plt

class backtester:
    """
    Backtester tests the model on historical data.
    """
    def __init__(self, date_files):
        """
        date_file - path to historical data (.csv)
        
        Initializes the backtest to historical data (price and time).
        """
        date_col_names = ['time', 'open', 'high', 'low', 'close', 'sep1', 
                          'sep2', 'sep3', 'sep4', 'sep5', 'sep6', 'sep7'] #Binance type
        self.date_high_arr  = np.array([])
        self.date_low_arr   = np.array([])
        self.date_time_arr  = np.array([])
        for file in date_files:
            date_csv = pd.read_csv(file, names=date_col_names)
            self.date_high_arr  = np.concatenate([self.date_high_arr, np.array(date_csv['high'])])
            self.date_low_arr   = np.concatenate([self.date_low_arr, np.array(date_csv['low'])])
            self.date_time_arr  = np.concatenate([self.date_time_arr,
                              np.array([datetime.fromtimestamp(date/1000) for date in date_csv['time']])])
    def parse_signals(self, signal_files):
        signal_col_names = ['signal', 'type', 'price', 'sep1', 'sep2', 
                            'date_string', 'date_ymd','date_hms', 'sep3'] #sample type
        signal_signals_arr     = np.array([])
        signal_price_arr       = np.array([])
        signal_time_arr        = np.array([])
        for file in signal_files:
            signal_csv = pd.read_csv(file,names=signal_col_names, delimiter=' ')
            signal_signals_arr = np.concatenate([signal_signals_arr, np.array(signal_csv['signal'])])
            signal_price_arr   = np.concatenate([signal_price_arr, np.array(signal_csv['price'])])
            date_ymd_arr       = np.array(signal_csv['date_ymd'])
            date_hms_arr       = np.array(signal_csv['date_hms'])
            signal_time_arr    = np.concatenate([signal_time_arr,
                                 np.array([datetime.strptime(date, '%Y-%m-%d %H:%M:%S') 
                                 for date in date_ymd_arr + ' ' + date_hms_arr])])
        return signal_signals_arr, signal_price_arr, signal_time_arr
        
        
    
    def backtesting(self, depo, depo_rate, stop_loss, leverage,
                    signal_signals_arr, signal_price_arr, signal_time_arr):
        assert len(self.date_time_arr) != 0, "Empty historical data"
        #info
        date_time_arr = self.date_time_arr
        date_low_arr  = self.date_low_arr
        date_high_arr = self.date_high_arr
        start_time    = date_time_arr[0]

        #order
        open_pos   = 'CLOSE'
        open_s     = 'NO'
        open_price = 0.0
        need_price = 0.0

        #deposit
        start_margin = depo
        self.margin       = start_margin

        #calc pnls
        pnl_pnl  = [0]
        pnl_time = [start_time]
        pnl_depo = [self.margin]
        uk_signal = 0

        #model info
        max_drawdown   = [0, start_time]
        min_margin_all = [start_margin, start_time]
        self.trades_profit  = 0
        self.trades_loss    = 0
        average_pnl    = 0
        end_margin     = 0
        drawndowns     = []
        
        def update_depo(per_profit):
            #global margin, trades_loss, trades_profit
            if per_profit < 0:
                self.trades_loss += 1
            else:
                self.trades_profit += 1
            pnl_pnl.append(pnl_pnl[-1] + per_profit)
            pnl_time.append(date_time_arr[uk_date])
            volume = depo_rate / 100 * self.margin * leverage
            profit = volume * per_profit
            self.margin += profit
            pnl_depo.append(self.margin)
        
        print("Start Backtest")
        for uk_date in tqdm(range(len(date_time_arr))):
            #margin_call
            if open_pos == 'OPEN':
                per_profit = (self.date_low_arr[uk_date] - open_price) / open_price
                volume = depo_rate / 100 * self.margin * leverage
                profit = volume * per_profit
                if per_profit < max_drawdown[0]:
                    max_drawdown = [per_profit, date_time_arr[uk_date]]
                if self.margin + profit < min_margin_all[0]:
                    min_margin_all = [self.margin + profit, date_time_arr[uk_date]]
                drawndowns[-1] = min(drawndowns[-1], per_profit * 100)
                if (self.margin + profit <= 0):
                    print("MARGIN_CALL", date_time_arr[uk_date])
                    break

            #new order
            if (uk_signal < len(signal_time_arr) and (date_time_arr[uk_date] > signal_time_arr[uk_signal])):
                #print(uk_signal)
                if signal_signals_arr[uk_signal] == 'OPEN':
                    if open_pos == 'OPEN':
                        per_profit = (date_high_arr[uk_date] - open_price) / open_price
                        update_depo(per_profit)
                        open_pos = 'CLOSE'
                    need_price = signal_price_arr[uk_signal]
                    open_pos   = 'WAIT'
                    open_s     = 'OPEN'
                    uk_signal += 1
                    continue
                if signal_signals_arr[uk_signal] == 'CLOSE':
                    if open_pos == 'WAIT' or open_pos == 'CLOSE':
                        uk_signal += 1
                        continue
                    need_price = signal_price_arr[uk_signal]
                    open_pos = 'WAIT'
                    open_s   = 'CLOSE'
                    uk_signal += 1
                    continue

            #stop_loss
            if open_pos == 'OPEN' and (date_low_arr[uk_date] - open_price) / open_price <= -stop_loss / 100:
                open_pos = 'CLOSE'
                per_profit = -stop_loss/100
                update_depo(per_profit)
                continue

            #trade
            if open_pos == 'WAIT' and need_price > date_high_arr[uk_date]:
                if open_s == 'OPEN':
                    open_price = need_price
                    open_s     = 'NO'
                    open_pos   = 'OPEN'
                    drawndowns.append(0)
                    continue
                if open_s == 'CLOSE':
                    per_profit = (need_price - open_price) / open_price
                    update_depo(per_profit)
                    open_s   = 'NO'
                    open_pos = 'CLOSE'
                    continue
        end_margin   = pnl_depo[-1]
        average_pnl  = (end_margin - start_margin) / (self.trades_profit + self.trades_loss) if self.trades_profit + self.trades_loss != 0 else 0

        time.sleep(0.1)
        print("End Backtest")
        return start_margin, end_margin,  min_margin_all, drawndowns, average_pnl, pnl_pnl, pnl_time, pnl_depo

        
    
    def test(self, name="Model", depo=1000, depo_rate=10, stop_loss=5, leverage=1, signal_files=[]):
        """
        name      - name model (string)
        depo      - volume deposit
        depo_rate - deposit percentage for trade (%)
        stop_loss - stop loss (%)
        leverage  - leverage 
        signals   - path to singals data (.csv)
        """
        signal_signals_arr, signal_price_arr, signal_time_arr = self.parse_signals(signal_files)
        
        start_margin, end_margin,  min_margin_all, drawndowns, average_pnl, pnl_pnl, pnl_time, pnl_depo = self.backtesting(depo, depo_rate, stop_loss, leverage, 
                         signal_signals_arr, signal_price_arr, signal_time_arr)
        
        print(f"Name: {name}")
        print(f"Options. Leverage: {leverage}, stop_loss: {stop_loss}%, depo rate: {depo_rate}%\n------")
        print(f"Start depo: {start_margin}, Finish depo: {round(end_margin, 2)}")
        print(f"Profit: {round(end_margin - start_margin, 2)} ({round(end_margin / start_margin, 2)}%), Average profit: {round(average_pnl, 2)} on trade")
        print(f"Max drawndown depo: {round(min_margin_all[0], 2)} {min_margin_all[1]}")
        print(f"Max drawndown trade: {round(np.min(drawndowns), 2)}%, average drawndown trade: {round(np.mean(drawndowns), 2)}%,")
        print(f"Amount trades: {self.trades_profit + self.trades_loss}, profit: {self.trades_profit}, loss: {self.trades_loss}")
        def sharpe(pnl):
            returns = np.array(pnl[1:]) - np.array(pnl[:-1])
            return np.mean(returns) / np.std(returns)
        print(f"Sharpe: {sharpe(pnl_pnl)}")

        plt.figure(figsize = (12, 10))
        plt.plot(self.date_time_arr, self.date_low_arr)
        plt.scatter(signal_time_arr[::2], signal_price_arr[::2], color='g', label='Buy', zorder=3, marker='^')
        plt.scatter(signal_time_arr[1::2], signal_price_arr[1::2], color='r', label='Sell', zorder=3,  marker='v')
        plt.plot(signal_time_arr, signal_price_arr)
        plt.title("Signals")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.legend()
        plt.show()

        plt.figure(figsize = (12, 10))
        plt.plot(pnl_time, pnl_depo, label=name)
        plt.title("Deposit")
        plt.xlabel("Time")
        plt.ylabel("Deposit")
        plt.legend()
        plt.show()
        
        return
    
    def multitest(self, params):
        """
        params - array of params. Example: [["model1",1000, 30, 1, 100, signal_files],
                                           ["model2", 1000, 30, 10, 5, signal_files]]
        Returns the profit graph of multiple models
        """
        plt.figure(figsize = (12, 10))
        for param in params:
            name, depo, depo_rate, leverage, stop_loss,  signal_files = param
            signal_signals_arr, signal_price_arr, signal_time_arr = self.parse_signals(signal_files)
            start_margin, end_margin,  min_margin_all, drawndowns, average_pnl, pnl_pnl, pnl_time, pnl_depo = self.backtesting(depo, depo_rate, stop_loss, leverage, 
                         signal_signals_arr, signal_price_arr, signal_time_arr)
            plt.plot(pnl_time, pnl_depo, label=name)
        plt.title("Deposit")
        plt.xlabel("Time")
        plt.ylabel("Deposit")
        plt.legend()
        plt.show()
