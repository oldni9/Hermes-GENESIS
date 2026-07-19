"""
===============================================================================
Unit tests for ProviderToolAdapter
===============================================================================
"""

import pytest
from hermes.ai.adapters.provider_tool_adapter import ProviderToolAdapter
from hermes.ai.response import ToolCall as ProviderToolCall, FunctionCall
from hermes.ai.tool import ToolStatus


class TestNormalizeArguments:
    def test_dict(self):
        assert ProviderToolAdapter.normalize_arguments({"a": 1}) == {"a": 1}

    def test_json_object(self):
        assert ProviderToolAdapter.normalize_arguments('{"b": 2}') == {"b": 2}

    def test_json_array(self):
        assert ProviderToolAdapter.normalize_arguments('[1,2,3]') == {"arg": [1,2,3]}

    def test_json_primitive(self):
        assert ProviderToolAdapter.normalize_arguments('42') == {"arg": 42}
        assert ProviderToolAdapter.normalize_arguments('true') == {"arg": True}

    def test_empty_string(self):
        assert ProviderToolAdapter.normalize_arguments("") == {}

    def test_whitespace(self):
        assert ProviderToolAdapter.normalize_arguments("   ") == {}

    def test_none(self):
        assert ProviderToolAdapter.normalize_arguments(None) == {}

    def test_raw_string(self):
        assert ProviderToolAdapter.normalize_arguments("hello") == {"arg": "hello"}

    def test_malformed_json(self):
        assert ProviderToolAdapter.normalize_arguments('{invalid') == {"arg": "{invalid"}

    def test_unsupported_type(self):
        assert ProviderToolAdapter.normalize_arguments([1,2]) is None
        assert ProviderToolAdapter.normalize_arguments(123) is None
        assert ProviderToolAdapter.normalize_arguments(object()) is None


class TestConvertProviderToolCalls:
    def test_single_call(self):
        calls = [
            ProviderToolCall(id="1", function=FunctionCall(name="test", arguments={"x": 1}))
        ]
        converted, errors = ProviderToolAdapter.convert_provider_tool_calls(calls)
        assert len(converted) == 1
        assert converted[0].id == "1"
        assert converted[0].tool_name == "test"
        assert converted[0].arguments == {"x": 1}
        assert not errors

    def test_multiple_calls_order(self):
        calls = [
            ProviderToolCall(id="a", function=FunctionCall(name="t1", arguments={})),
            ProviderToolCall(id="b", function=FunctionCall(name="t2", arguments={})),
        ]
        converted, errors = ProviderToolAdapter.convert_provider_tool_calls(calls)
        assert len(converted) == 2
        assert converted[0].id == "a"
        assert converted[1].id == "b"

    def test_mixed_conversion(self):
        calls = [
            ProviderToolCall(id="good", function=FunctionCall(name="ok", arguments={"x": 1})),
            ProviderToolCall(id="bad", function=FunctionCall(name="fail", arguments=[1,2])),
        ]
        converted, errors = ProviderToolAdapter.convert_provider_tool_calls(calls)
        assert len(converted) == 1
        assert converted[0].id == "good"
        assert len(errors) == 1
        assert errors[0].call_id == "bad"
        assert errors[0].status == ToolStatus.FAILED
        assert "Invalid arguments" in errors[0].error

    def test_json_string_argument(self):
        calls = [
            ProviderToolCall(id="json", function=FunctionCall(name="test", arguments='{"a":1}'))
        ]
        converted, errors = ProviderToolAdapter.convert_provider_tool_calls(calls)
        assert len(converted) == 1
        assert converted[0].arguments == {"a": 1}
        assert not errors