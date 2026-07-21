import pytest
import tempfile
from hermes.tools import calculate, get_current_time, FileTools
from hermes.filesystem import LocalFilesystem

def test_math_tool_basic():
    assert calculate.function("2 + 3 * 4") == "14"

def test_math_tool_rejects_code():
    with pytest.raises(ValueError):
        calculate.function("__import__('os').system('ls')")

def test_time_tool():
    assert "T" in get_current_time.function()

def test_file_tools():
    with tempfile.TemporaryDirectory() as tmpdir:
        fs = LocalFilesystem(tmpdir)
        file_tools = FileTools(fs)
        write_tool = next(t for t in file_tools.tools if t.name == "write_file")
        read_tool = next(t for t in file_tools.tools if t.name == "read_file")
        assert "Successfully wrote" in write_tool.function(path="test.txt", content="Hello World")
        assert read_tool.function(path="test.txt") == "Hello World"