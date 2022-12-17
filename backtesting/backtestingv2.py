from .backtesting import Strategy
from .tlib import SMA, RSI
from .udf_parser import parse_udf
from enum import Enum
import operator

class Action(Enum):
    BUY = 1
    SELL = 2
    WAIT = 3

func_maps = {
    "RSI": RSI,
    "MA": SMA
}

ops_maps = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.le,
    "<=": operator.ge,
    "==": operator.eq,
}

def concat_attr_name(fn, args):
    return fn + "_".join([str(arg) for arg in args])


class StrategyWithContext(Strategy):
    context = None
    udf = None
    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.udf = self._params["udf"]
        if "context" in self._params:
            self.context = self._params["context"]

    def init(self):
        self.load_udf(self.udf["buy_udf"], self.udf["sell_udf"])

    def load_udf(self, buy_udf: str, sell_udf: str):
        self._buy_udf = parse_udf(buy_udf)
        for dep in self._buy_udf["deps"]:
            attr_name = concat_attr_name(dep["name"], dep["args"])
            if not hasattr(self, attr_name):
                self.__setattr__(attr_name, self.I(func_maps[dep["name"]], self.data, *dep["args"]))
        self._sell_udf = parse_udf(sell_udf)
        for dep in self._sell_udf["deps"]:
            attr_name = concat_attr_name(dep["name"], dep["args"])
            if not hasattr(self, attr_name):
                self.__setattr__(attr_name, self.I(func_maps[dep["name"]], self.data, *dep["args"]))

    def get_val(self, sta):
        atype = sta["type"]
        if atype == "ivalue":
            return sta["value"]
        elif atype == "func":
            attr_name = concat_attr_name(sta["name"], sta["args"])
            return self.__getattribute__(attr_name)[-1]
        elif atype == "price":
            return self.data[sta["value"]]
    
    def get_a_b(self, sta):
        a = self.get_val(sta["a"])
        b = self.get_val(sta["b"])
        return a,b
        
    # we should move into 3.10 for match syntax
    def next_and(self, stas):
        for sta in stas:
            op_func = ops_maps[sta["op"]]
            a, b = self.get_a_b(sta)
            if not op_func(a, b):
                return False
        return True

    def next_or(self, stas):
        for sta in stas:
            op_func = ops_maps[sta["op"]]
            a, b = self.get_a_b(sta)
            if op_func(a, b):
                return True
        return False

    def next(self):
        if self._buy_udf["cond"] == "or":
            if_buy = self.next_or(self._buy_udf["statements"])
        else:
            if_buy = self.next_and(self._buy_udf["statements"])
        if if_buy:
            self.buy()

        if self._sell_udf["cond"] == "or":
            if_sell = self.next_or(self._sell_udf["statements"])
        else:
            if_sell = self.next_and(self._sell_udf["statements"])
        if if_sell:
            self.sell()