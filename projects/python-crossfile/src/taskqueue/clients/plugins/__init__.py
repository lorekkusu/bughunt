"""Plugin discovery and loading.

Plugins are *not* imported statically anywhere in the service. They register
themselves via the :func:`register` decorator when their module is imported,
and deployments choose which modules to import through the ``plugins`` config
key (a comma-separated module list). This keeps the core free of dependencies
on any particular plugin.
"""

from __future__ import annotations

import importlib
import inspect
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from taskqueue.clients.plugins.base import Plugin

_REGISTRY: dict[str, Type["Plugin"]] = {}


def register(cls: Type["Plugin"]) -> Type["Plugin"]:
    """Class decorator: make *cls* loadable by name."""
    _REGISTRY[cls.name] = cls
    return cls


def registered_names() -> list[str]:
    return sorted(_REGISTRY)


def load_plugins(module_names: list[str], **kwargs) -> list["Plugin"]:
    """Import each module (triggering registration) and instantiate its plugins.

    *kwargs* are passed to every plugin constructor that accepts them; plugins
    take only the keyword arguments they declare.
    """
    for module_name in module_names:
        importlib.import_module(module_name)
    wanted = set(module_names)
    instances: list["Plugin"] = []
    for name in sorted(_REGISTRY):
        cls = _REGISTRY[name]
        # The registry is process-wide; only instantiate plugins that belong
        # to the modules this deployment asked for.
        if cls.__module__ not in wanted:
            continue
        parameters = inspect.signature(cls).parameters
        accepted = {key: value for key, value in kwargs.items() if key in parameters}
        instances.append(cls(**accepted))
    return instances
