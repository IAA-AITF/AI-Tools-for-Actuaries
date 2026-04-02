"""Compatibility shim for legacy imports.

Prefer importing from ``doc_to_md.config.settings``.
"""

from doc_to_md.config.settings import EngineName, Settings, get_settings

__all__ = ["EngineName", "Settings", "get_settings"]
