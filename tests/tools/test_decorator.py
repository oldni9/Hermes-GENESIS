import pytest
from hermes.tools import tool, Tool, ToolParameter, ParameterType

def test_tool_decorator_basic():
    @tool(name="test_tool", description="A test tool")
    def my_func(x: int, y: str = "default") -> str: return f"{x}{y}"
    assert isinstance(my_func, Tool)
    assert my_func.name == "test_tool"
    assert len(my_func.parameters) == 2
    p1 = my_func.parameters[0]
    assert p1.name == "x"
    assert p1.type == ParameterType.INTEGER
    assert p1.required is True
    p2 = my_func.parameters[1]
    assert p2.name == "y"
    assert p2.type == ParameterType.STRING
    assert p2.required is False

def test_tool_decorator_skips_self():
    @tool(name="method_tool")
    def my_method(self, x: int): return x
    assert len(my_method.parameters) == 1
    assert my_method.parameters[0].name == "x"