"""
ClawNet — Context Consistency Protocol for Agent Systems

The infrastructure layer that multi-agent systems need but nobody built.
Not another framework. The protocol that makes them all work together.

pip install clawnet
"""

__version__ = "2.0.0"
__protocol__ = "context-consistency-v2"

from .client import ClawNetClient, ClawNetBridge
from .protocol import ClawNetProtocol, ContextLockManager, ContextLineage

# Convenience function
def connect(endpoint: str = "localhost:7890"):
    """Quick connect to ClawNet server."""
    return ClawNetClient("default", "agent", server=endpoint)
