"""
Conversation context manager — future-ready scaffold.

Phase 1: Minimal implementation that tracks tool calls and data sources
used within a single conversation. Not yet wired into the main flow.

Future phases will add:
- Package Workspace state
- Session persistence
- Multi-turn context enrichment
"""

from typing import Any, Dict, List, Optional


class ConversationContext:
    """Manages conversation state for the AI module."""

    def __init__(self):
        self.tool_calls_history: List[Dict[str, Any]] = []
        self.data_sources_used: List[str] = []
        self._verified_data: Dict[str, Any] = {}

    def record_tool_call(
        self,
        tool_name: str,
        args: dict,
        result: dict,
        confidence: str = "Unknown",
    ) -> None:
        """Record a tool call for context tracking."""
        self.tool_calls_history.append({
            "tool": tool_name,
            "args": args,
            "confidence": confidence,
        })
        if tool_name not in self.data_sources_used:
            self.data_sources_used.append(tool_name)

    def store_verified_data(self, key: str, value: Any) -> None:
        """Store a verified data point for cross-reference in later turns."""
        self._verified_data[key] = value

    def get_verified_data(self, key: str) -> Optional[Any]:
        """Retrieve a previously verified data point."""
        return self._verified_data.get(key)

    def get_data_summary(self) -> dict:
        """Return summary of all data sources used in this conversation."""
        return {
            "total_tool_calls": len(self.tool_calls_history),
            "data_sources": self.data_sources_used,
            "verified_data_keys": list(self._verified_data.keys()),
        }

    def reset(self) -> None:
        """Clear all context state."""
        self.tool_calls_history.clear()
        self.data_sources_used.clear()
        self._verified_data.clear()
