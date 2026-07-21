from __future__ import annotations
import inspect
from typing import Any, Callable, Optional
from hermes.ai.tool import Tool, ToolParameter, _infer_parameter_from_annotation

def tool(name: str, description: str = "", namespace: Optional[str] = None, category: Optional[str] = None) -> Callable:
    def decorator(func: Callable) -> Tool:
        sig = inspect.signature(func)
        params = []
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls", "context"): continue
            annotation = param.annotation if param.annotation is not inspect._empty else Any
            default = param.default if param.default is not inspect._empty else None
            param_obj = _infer_parameter_from_annotation(param_name, annotation, default)
            param_obj.required = param.default is inspect._empty
            params.append(param_obj)
        return Tool(name=name, namespace=namespace, description=description or func.__doc__ or "", parameters=params, function=func, category=category)
    return decorator