from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import GOOG
from backtesting.tlib import SMA, RSI
import pandas as pd
from dataclasses import dataclass, field, fields


class SmaCross(Strategy):
    def init(self):
        self.ma1 = self.I(SMA, self.data, 10)
        self.ma2 = self.I(SMA, self.data, 20)
        self.rsi14 = self.I(RSI,self.data, 14)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()


bt = Backtest(GOOG, SmaCross, commission=.002,
              exclusive_orders=True)
stats = bt.run()
print(stats)