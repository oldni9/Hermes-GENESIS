import ast
import operator
from hermes.tools.decorators import tool

ALLOWED_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.UAdd: operator.pos, ast.Mod: operator.mod,
}

def _safe_math_eval(expression: str) -> float:
    try: tree = ast.parse(expression, mode='eval')
    except SyntaxError: raise ValueError("Invalid mathematical expression")
    def _eval(node):
        if isinstance(node, ast.Expression): return _eval(node.body)
        elif isinstance(node, ast.BinOp):
            op = ALLOWED_OPERATORS.get(type(node.op))
            if not op: raise ValueError(f"Unsupported operator: {type(node.op)}")
            return op(_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            op = ALLOWED_OPERATORS.get(type(node.op))
            if not op: raise ValueError(f"Unsupported operator: {type(node.op)}")
            return op(_eval(node.operand))
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)): return node.value
            raise ValueError("Only numbers are allowed")
        else: raise ValueError(f"Unsupported syntax: {type(node)}")
    return _eval(tree)

@tool(name="calculate", description="Safely evaluate a mathematical expression.")
def calculate(expression: str) -> str:
    return str(_safe_math_eval(expression))