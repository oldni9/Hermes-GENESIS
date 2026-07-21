# debug_test.py
import tempfile
from hermes.tools import ToolManager, ToolRegistry
from hermes.workspace.workspace import Workspace
from hermes.filesystem import LocalFilesystem

print("--- Starting Debug ---")

with tempfile.TemporaryDirectory() as tmpdir:
    tm = ToolManager(ToolRegistry())
    fs = LocalFilesystem(tmpdir)
    ws = Workspace(filesystem=fs, tool_manager=tm)
    
    print(f"Workspace ID: {ws.workspace_id}")
    print(f"Expected Tool Name: {ws.workspace_id}.read_file")
    
    print("\n--- Tools in Registry ---")
    names = tm.full_names()
    print(f"Full Names: {names}")
    
    print("\n--- Checking Exists ---")
    exists_result = tm.exists(f"{ws.workspace_id}.read_file")
    print(f"tm.exists('{ws.workspace_id}.read_file'): {exists_result}")
    
    print("\n--- Checking Registry Internals ---")
    print(f"Registry _tools keys: {list(tm._registry._tools.keys())}")
    print(f"Registry _aliases: {tm._registry._aliases}")
    
    print(repr(ws.workspace_id))
    print(repr(tm.full_names()))

print("--- Debug Finished ---")