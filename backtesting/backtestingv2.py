from .backtesting import Strategy
class StrategyWithContext(Strategy):
    context = None
    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.context = self._params["context"]

