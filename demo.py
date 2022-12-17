from backtesting import Backtest, StrategyWithContext
from backtesting.test import GOOG


bt = Backtest(GOOG, StrategyWithContext, exclusive_orders=True)
stats = bt.run(udf={
    "buy_udf": "RSI(14) > 70",
    "sell_udf": "RSI(14) < 30"
})
print(stats)