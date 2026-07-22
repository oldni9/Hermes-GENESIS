"""
===============================================================================
Tests for Planner Registry & Factory
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from hermes.agent.executor.planners.registry import (
    PlannerRegistry, 
    PlannerFactory, 
    PlannerDescriptor,
    PlannerCapabilities,
    GLOBAL_PLANNER_REGISTRY,
    GLOBAL_PLANNER_FACTORY
)
from hermes.agent.executor.planners.react import ReActPlanner
from hermes.agent.executor.planners.reflection import ReflectionPlanner
from hermes.agent.executor.errors import PlannerError
from hermes.bootstrap.bootstrap import register_builtin_planners


@pytest.fixture
def empty_registry():
    return PlannerRegistry()

def test_register_and_get(empty_registry):
    desc = PlannerDescriptor(name="react", planner_class=ReActPlanner)
    empty_registry.register(desc)
    
    assert empty_registry.contains("react")
    fetched = empty_registry.get("react")
    assert fetched.planner_class == ReActPlanner

def test_register_normalizes_names(empty_registry):
    desc = PlannerDescriptor(name="ReAct", planner_class=ReActPlanner, aliases=["Default"])
    empty_registry.register(desc)
    
    assert empty_registry.contains("react")
    assert empty_registry.contains("REACT")
    assert empty_registry.contains("default")
    assert empty_registry.get("react").name == "react"

def test_register_invalid_class_raises(empty_registry):
    class NotAPlanner:
        pass
        
    desc = PlannerDescriptor(name="bad", planner_class=NotAPlanner)
    with pytest.raises(PlannerError, match="not a subclass of Planner"):
        empty_registry.register(desc)

def test_freeze_prevents_modification(empty_registry):
    empty_registry.register(PlannerDescriptor(name="react", planner_class=ReActPlanner))
    empty_registry.freeze()
    
    with pytest.raises(PlannerError, match="Registry is frozen"):
        empty_registry.register(PlannerDescriptor(name="reflection", planner_class=ReflectionPlanner))
        
    with pytest.raises(PlannerError, match="Registry is frozen"):
        empty_registry.unregister("react")
        
    with pytest.raises(PlannerError, match="Registry is frozen"):
        empty_registry.clear()

def test_capabilities_metadata():
    caps = PlannerCapabilities(reflection=True, tree_search=True)
    desc = PlannerDescriptor(name="tot", planner_class=ReActPlanner, capabilities=caps)
    
    assert desc.capabilities.reflection is True
    assert desc.capabilities.tree_search is True
    assert desc.capabilities.parallel is False

def test_duplicate_registration_rejected(empty_registry):
    desc1 = PlannerDescriptor(name="react", planner_class=ReActPlanner)
    empty_registry.register(desc1)
    
    desc2 = PlannerDescriptor(name="react", planner_class=ReActPlanner)
    with pytest.raises(PlannerError, match="already registered"):
        empty_registry.register(desc2)

def test_factory_instantiation(empty_registry):
    empty_registry.register(PlannerDescriptor(name="react", planner_class=ReActPlanner))
    
    factory = PlannerFactory(empty_registry)
    react_planner = factory.create("react")
    assert isinstance(react_planner, ReActPlanner)

def test_factory_alias_instantiation(empty_registry):
    empty_registry.register(PlannerDescriptor(name="react", planner_class=ReActPlanner, aliases=["default"]))
    
    factory = PlannerFactory(empty_registry)
    react_planner = factory.create("default")
    assert isinstance(react_planner, ReActPlanner)

def test_descriptors_returns_unique(empty_registry):
    empty_registry.register(PlannerDescriptor(name="react", planner_class=ReActPlanner, aliases=["default"]))
    empty_registry.register(PlannerDescriptor(name="reflection", planner_class=ReflectionPlanner))
    
    descriptors = empty_registry.descriptors()
    assert len(descriptors) == 2
    names = [d.name for d in descriptors]
    assert "react" in names
    assert "reflection" in names
    assert "default" not in names

def test_bootstrap_freezes_global_registry():
    """Ensure that calling bootstrap freezes the global registry."""
    GLOBAL_PLANNER_REGISTRY.reset_for_testing()
    register_builtin_planners()
    
    assert GLOBAL_PLANNER_REGISTRY._frozen is True
    
    with pytest.raises(PlannerError, match="Registry is frozen"):
        GLOBAL_PLANNER_REGISTRY.register(PlannerDescriptor(name="test", planner_class=ReActPlanner))

def test_global_factory_lookup():
    """Ensure the global factory can instantiate built-in planners."""
    GLOBAL_PLANNER_REGISTRY.reset_for_testing()
    register_builtin_planners()
    
    react_planner = GLOBAL_PLANNER_FACTORY.create("react")
    assert isinstance(react_planner, ReActPlanner)
    
    default_planner = GLOBAL_PLANNER_FACTORY.create("default")
    assert isinstance(default_planner, ReActPlanner)