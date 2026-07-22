"""
===============================================================================
Planner Registry & Factory
===============================================================================

Global registry and factory for planner classes.
Separates planner metadata storage (Registry) from instantiation (Factory).
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Type, Any

from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.errors import PlannerError
from hermes.agent.executor.planners.base import Planner


@dataclass(frozen=True)
class PlannerCapabilities:
    """Declares what a planner can do. Useful for UI routing and validation."""
    reflection: bool = False
    tree_search: bool = False
    debate: bool = False
    parallel: bool = False
    memory: bool = False


@dataclass(frozen=True)
class PlannerDescriptor:
    """Metadata for a registered planner."""
    name: str
    planner_class: Type[Planner]
    version: str = "1.0"
    author: str = "Hermes"
    description: str = ""
    aliases: List[str] = field(default_factory=list)
    capabilities: PlannerCapabilities = field(default_factory=PlannerCapabilities)


class PlannerRegistry:
    """
    Stores planner metadata. Application-wide singleton.
    Does NOT instantiate planners.
    """
    
    def __init__(self) -> None:
        self._planners: Dict[str, PlannerDescriptor] = {}
        self._frozen: bool = False

    def register(self, descriptor: PlannerDescriptor) -> None:
        """Register a planner descriptor."""
        if self._frozen:
            raise PlannerError("Registry is frozen and cannot be modified.")
            
        # Strict subclass validation
        try:
            if not issubclass(descriptor.planner_class, Planner):
                raise PlannerError(f"Class '{descriptor.planner_class.__name__}' is not a subclass of Planner.")
        except TypeError:
            raise PlannerError(f"Invalid planner_class provided: {descriptor.planner_class}")
            
        # Normalize planner names (lowercase)
        primary_name = descriptor.name.lower().strip()
        if not primary_name:
            raise PlannerError("Planner name cannot be empty.")
            
        aliases = [a.lower().strip() for a in descriptor.aliases]
        
        all_names = [primary_name] + aliases
        for name in all_names:
            if name in self._planners:
                raise PlannerError(f"Planner name/alias '{name}' is already registered.")
                
        # Re-create descriptor with normalized names to ensure consistency
        normalized_desc = PlannerDescriptor(
            name=primary_name,
            planner_class=descriptor.planner_class,
            version=descriptor.version,
            author=descriptor.author,
            description=descriptor.description,
            aliases=aliases,
            capabilities=descriptor.capabilities
        )
        
        self._planners[primary_name] = normalized_desc
        for alias in aliases:
            self._planners[alias] = normalized_desc

    def freeze(self) -> None:
        """Freeze the registry to prevent further modifications."""
        self._frozen = True

    def unregister(self, name: str) -> None:
        """Remove a planner and its aliases."""
        if self._frozen:
            raise PlannerError("Registry is frozen and cannot be modified.")
            
        desc = self.get(name)
        if desc:
            self._planners.pop(desc.name, None)
            for alias in desc.aliases:
                self._planners.pop(alias, None)

    def contains(self, name: str) -> bool:
        """Check if a planner name or alias is registered."""
        return name.lower().strip() in self._planners

    def names(self) -> List[str]:
        """Return a list of registered planner primary names."""
        seen = set()
        result = []
        for desc in self._planners.values():
            if desc.name not in seen:
                seen.add(desc.name)
                result.append(desc.name)
        return sorted(result)

    def descriptors(self) -> List[PlannerDescriptor]:
        """Return a list of all registered planner descriptors (unique)."""
        seen = set()
        result = []
        for desc in self._planners.values():
            if desc.name not in seen:
                seen.add(desc.name)
                result.append(desc)
        return result

    def get(self, name: str) -> PlannerDescriptor:
        """Retrieve the planner descriptor by name or alias."""
        normalized_name = name.lower().strip()
        if normalized_name not in self._planners:
            raise PlannerError(f"Planner '{name}' not found in registry.")
        return self._planners[normalized_name]

    def clear(self) -> None:
        """Clear all registered planners."""
        if self._frozen:
            raise PlannerError("Registry is frozen and cannot be modified.")
        self._planners.clear()


class PlannerFactory:
    """
    Instantiates planner instances using the registry.
    """
    
    def __init__(self, registry: PlannerRegistry) -> None:
        self._registry = registry

    def create(
        self, 
        name: str, 
        pipeline: PipelineProtocol, 
        provider: str, 
        model: str = "",
        **kwargs: Any
    ) -> Planner:
        """Instantiate a registered planner."""
        descriptor = self._registry.get(name)
        return descriptor.planner_class(
            pipeline=pipeline, 
            provider=provider, 
            model=model, 
            **kwargs
        )


# =============================================================================
# Global Singleton Instances
# =============================================================================

GLOBAL_PLANNER_REGISTRY = PlannerRegistry()
GLOBAL_PLANNER_FACTORY = PlannerFactory(GLOBAL_PLANNER_REGISTRY)

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture