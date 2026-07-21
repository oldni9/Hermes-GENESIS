"""
===============================================================================
Tests for ToolRegistry
===============================================================================
"""

import pytest
import threading
import random
from hermes.tools import Tool, ToolRegistry, ToolError


@pytest.fixture
def registry():
    return ToolRegistry()

def make_tool(name="test_tool", namespace=None, aliases=None, description=""):
    return Tool(
        name=name, 
        namespace=namespace, 
        function=lambda: None,
        aliases=aliases or [],
        description=description
    )

def test_register_and_get(registry):
    tool = make_tool(name="calc")
    registry.register(tool)
    assert registry.get("calc") is tool

def test_alias_lookup_global(registry):
    tool = make_tool(name="calculate", aliases=["calc", "math"])
    registry.register(tool)
    assert registry.get("calc") is tool
    assert registry.get("math") is tool

def test_namespaced_alias_lookup(registry):
    tool = make_tool(name="read_file", namespace="ws_123", aliases=["rf"])
    registry.register(tool)
    
    # Short alias should not work globally for namespaced tools
    assert registry.get("rf") is None
    
    # Namespaced alias should work
    assert registry.get("ws_123.rf") is tool

def test_duplicate_alias_rejected(registry):
    """Test that registering duplicate aliases raises an error."""
    t1 = make_tool(name="calc1", aliases=["c"])
    registry.register(t1)
    
    t2 = make_tool(name="calc2", aliases=["c"])
    with pytest.raises(ToolError, match="Alias 'c' is already registered"):
        registry.register(t2)

def test_registry_replace(registry):
    tool1 = make_tool(name="calc")
    registry.register(tool1)
    
    tool2 = make_tool(name="calc")
    registry.replace(tool2)
    
    assert registry.get("calc") is tool2

def test_registry_replace_safe_on_failure(registry):
    """Test that replace does not delete the old tool if new tool validation fails."""
    tool1 = make_tool(name="calc", aliases=["c1"])
    registry.register(tool1)
    
    # tool2 has an alias that collides with an existing global tool
    tool2 = make_tool(name="calc2", aliases=["c1"])
    
    with pytest.raises(ToolError):
        registry.replace(tool2)
        
    # Original tool should still be there
    assert registry.get("calc") is tool1

def test_registry_clear(registry):
    registry.register(make_tool(name="t1"))
    registry.register(make_tool(name="t2"))
    
    registry.clear()
    assert len(registry) == 0

def test_registry_search(registry):
    t1 = make_tool(name="search_web", description="Search the internet")
    t2 = make_tool(name="search_files", description="Search local files")
    t3 = make_tool(name="calculate", description="Do math")
    
    registry.register(t1)
    registry.register(t2)
    registry.register(t3)
    
    results = registry.search("search")
    assert len(results) == 2
    assert t1 in results
    assert t2 in results

def test_registry_names_and_namespaces(registry):
    registry.register(make_tool(name="t1", namespace="ws1"))
    registry.register(make_tool(name="t2", namespace="ws1"))
    registry.register(make_tool(name="t3", namespace="ws2"))
    registry.register(make_tool(name="global_tool"))
    
    assert set(registry.names()) == {"ws1.t1", "ws1.t2", "ws2.t3", "global_tool"}
    assert set(registry.namespaces()) == {"ws1", "ws2"}

def test_concurrent_stress_test(registry):
    """Stress test thread-safety with random operations."""
    threads = []
    errors = []

    def worker_thread(thread_id):
        try:
            for _ in range(100):
                op = random.choice(["register", "unregister", "get", "exists", "search"])
                
                if op == "register":
                    name = f"t_{thread_id}_{random.randint(0, 100)}"
                    tool = make_tool(name=name)
                    try:
                        registry.register(tool)
                    except ToolError:
                        pass  # Expected if already exists
                        
                elif op == "unregister":
                    name = f"t_{thread_id}_{random.randint(0, 100)}"
                    registry.unregister(name)
                    
                elif op == "get":
                    name = f"t_{thread_id}_{random.randint(0, 100)}"
                    registry.get(name)
                    
                elif op == "exists":
                    name = f"t_{thread_id}_{random.randint(0, 100)}"
                    registry.exists(name)
                    
                elif op == "search":
                    registry.search("t_")
                    
        except Exception as e:
            errors.append(e)

    # Spawn 15 threads
    for i in range(15):
        t = threading.Thread(target=worker_thread, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert len(errors) == 0

def test_iteration_is_snapshot(registry):
    """Test that iteration returns a snapshot and doesn't crash on mutation."""
    registry.register(make_tool(name="t1"))
    registry.register(make_tool(name="t2"))
    
    # Iterate and mutate simultaneously
    tools_iter = iter(registry)
    registry.register(make_tool(name="t3"))
    
    # This should not raise RuntimeError
    tools = list(tools_iter)
    assert len(tools) == 2  # Should only see the snapshot from when iter() was called

def test_lookup_precedence_global_vs_workspace(registry):
    """Test that global tools and workspace tools can coexist and lookup precedence is correct."""
    global_tool = make_tool(name="read_file", namespace=None)
    registry.register(global_tool)
    
    ws_tool = make_tool(name="read_file", namespace="ws_123")
    registry.register(ws_tool)
    
    # Lookup by short name returns global
    assert registry.get("read_file") is global_tool
    
    # Lookup by full name returns workspace
    assert registry.get("ws_123.read_file") is ws_tool