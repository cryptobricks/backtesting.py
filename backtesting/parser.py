from lark import Lark
udf_parser = Lark(r"""
cond: stat [(join stat)*]
join: "and" | "or"
op: ">" | "<" | "<=" | ">=" | "=="
indicator:function | price | SIGNED_NUMBER -> number
stat: indicator op indicator
function: name "(" args ")"
name: "RSI" | "MA"
args: arg [("," arg)*]
arg: SIGNED_NUMBER
price: "Close" | "Open" | "High" | "Low"
%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", start='cond')


def parse_udf(expression: str):
    result = udf_parser.parse(expression)
    return result


if __name__ == "__main__":
    s = "RSI(40) > 40 and RSI(20) < 30"
    res = parse_udf(s)
    print(res.pretty())