"""MCP tools indirection layer.

This module is the single import point for MCP tool loading.
Tests patch `mcp_tools.get_mcp_tools` to inject mock tools without
modifying any application code.
"""

from mcp_providers.agw import get_mcp_tools

__all__ = ["get_mcp_tools"]
