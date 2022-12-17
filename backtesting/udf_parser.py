from lark import Lark
from lark.visitors import Interpreter,Transformer
udf_parser = Lark(r"""
cond: stat [(join stat)*]
!join: "and" | "or"
!op: ">" | "<" | "<=" | ">=" | "=="
indicator:function | price | ivalue
stat: indicator op indicator
ivalue: SIGNED_NUMBER
function: name "(" args ")"
!name: "RSI" | "MA"
args: arg [("," arg)*]
arg: SIGNED_NUMBER -> number
!price: "Close" | "Open" | "High" | "Low"
%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", start='cond')

class WrongOps(Exception):
    pass

class StrategyBackend(Transformer):
    join_type = None
    def cond(self, args):
        args = [arg for arg in args if arg is not None]
        return args

    def join(self, tokens):
        val = tokens[0].value
        if self.join_type and self.join_type != val:
            raise WrongOps()
        else:
            self.join_type = val
    
    def indicator(self, args):
        return args[0]
    
    def stat(self, args):
        return {
            "op": args[1],
            "a": args[0],
            "b": args[2]
        }
    
    def op(self, tokens):
        return tokens[0].value

    def ivalue(self, args):
        return {
            "type": "ivalue",
            "value": float(args[0].value),
        }

    def number(self, n):
        (n,) = n
        return float(n)
    
    def function(self, args):
        return {
            "type": "func",
            "name": args[0],
            "args": args[1]
        }

    def price(self, args):
        return {
            "type": "price",
            "value": args[0].value
        }

    def args(self, args):
        return args
    
    def name(self, tokens):
        return tokens[0].value

def parse_udf(expression: str):
    result = udf_parser.parse(expression)
    return result

if __name__ == "__main__":
    s = "RSI(40, 20) > 40 and RSI(40) < Close"
    res = parse_udf(s)
    # print(res.pretty())
    sb = StrategyBackend()
    s = sb.transform(res)
    print(s)