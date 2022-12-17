from .backtesting import Strategy
from .udf_parser import parse_udf

class StrategyWithContext(Strategy):
    context = None
    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.context = self._params["context"]
    
    def load_udf(udf: str):
        ast = parse_udf(udf)
