"""
===============================================================================
Tests for Hermes ExecutionContext
===============================================================================
"""
from __future__ import annotations

import pytest
from hermes.core.context import ExecutionContext


class TestExecutionContext:
    def test_create_empty(self):
        ctx = ExecutionContext()
        assert ctx.configuration == {}
        assert ctx.conversation is None
        assert ctx.memory is None
        assert ctx.services is None
        assert ctx.provider is None
        assert ctx.model is None
        assert ctx.workflow is None
        assert ctx.agent is None
        assert ctx.trace is None
        assert ctx.variables == {}
        assert ctx.artifacts == {}
        assert ctx.metadata == {}

    def test_create_with_fields(self):
        ctx = ExecutionContext(
            configuration={"timeout": 30},
            provider="openai",
            model="gpt-4",
            variables={"x": 1},
            metadata={"user": "alice"},
        )
        assert ctx.configuration == {"timeout": 30}
        assert ctx.provider == "openai"
        assert ctx.model == "gpt-4"
        assert ctx.variables == {"x": 1}
        assert ctx.metadata == {"user": "alice"}

    def test_clone_deep(self):
        ctx = ExecutionContext(
            variables={"nested": {"a": 1}},
            artifacts={"list": [1, 2, 3]},
            configuration={"cfg": {"sub": 5}},
        )
        ctx2 = ctx.clone()
        # Modify original
        ctx.variables["nested"]["a"] = 999
        ctx.artifacts["list"].append(4)
        ctx.configuration["cfg"]["sub"] = 6
        # The clone should not be affected
        assert ctx2.variables["nested"]["a"] == 1
        assert ctx2.artifacts["list"] == [1, 2, 3]
        assert ctx2.configuration["cfg"]["sub"] == 5

    def test_clone_with_cloneable_object(self):
        # Mock object with clone method
        class MockCloneable:
            def __init__(self, val):
                self.val = val
            def clone(self):
                return MockCloneable(self.val)

        ctx = ExecutionContext(agent=MockCloneable(42))
        ctx2 = ctx.clone()
        assert ctx2.agent.val == 42
        assert ctx2.agent is not ctx.agent  # Should be a new instance

    def test_clone_with_non_cloneable_object(self):
        class NonCloneable:
            def __init__(self, val):
                self.val = val

        ctx = ExecutionContext(agent=NonCloneable(42))
        ctx2 = ctx.clone()
        # Should be the same reference (shallow copy)
        assert ctx2.agent is ctx.agent

    def test_to_dict(self):
        ctx = ExecutionContext(
            configuration={"cfg": 1},
            provider="test",
            variables={"var": 2},
        )
        d = ctx.to_dict()
        assert d["configuration"] == {"cfg": 1}
        assert d["provider"] == "test"
        assert d["variables"] == {"var": 2}

    def test_from_dict(self):
        data = {
            "configuration": {"cfg": 1},
            "provider": "test",
            "variables": {"var": 2},
            "metadata": {"user": "bob"},
        }
        ctx = ExecutionContext.from_dict(data)
        assert ctx.configuration == {"cfg": 1}
        assert ctx.provider == "test"
        assert ctx.variables == {"var": 2}
        assert ctx.metadata == {"user": "bob"}

    def test_copy_alias(self):
        ctx = ExecutionContext(provider="test")
        ctx2 = ctx.copy()
        assert ctx2.provider == "test"
        assert ctx2 is not ctx