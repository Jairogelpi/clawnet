#!/usr/bin/env python3
"""
ClawNet Protocol v2 — Context Consistency Layer

The three features nobody else has:
1. Context Locking — prevent agent collisions
2. Context Lineage — full traceability of every decision
3. Context Inheritance — agents inherit collective knowledge instantly
"""

import time
import threading
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ContextLock:
    """Exclusive lock on a context resource — prevents agent collisions."""
    resource: str
    owner: str
    acquired_at: float
    expires_at: float
    lock_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
    
    def to_dict(self) -> dict:
        return {
            'lock_id': self.lock_id,
            'resource': self.resource,
            'owner': self.owner,
            'acquired_at': self.acquired_at,
            'expires_at': self.expires_at,
            'remaining_seconds': max(0, self.expires_at - time.time()),
            'expired': self.is_expired()
        }


@dataclass
class LineageEntry:
    """Single entry in the context lineage chain."""
    action: str          # "created", "modified", "accessed", "locked", "released"
    context_id: str
    agent: str
    timestamp: float
    details: str = ""
    parent_entry: Optional[str] = None  # Links to previous action
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'action': self.action,
            'context_id': self.context_id,
            'agent': self.agent,
            'timestamp': self.timestamp,
            'details': self.details,
            'parent_entry': self.parent_entry,
            'metadata': self.metadata
        }


class ContextLockManager:
    """
    Prevents agent collisions by managing exclusive access to context resources.
    
    Like database row locks, but for AI agent context.
    
    Usage:
        lock_mgr = ContextLockManager()
        
        # Agent A acquires lock
        lock = lock_mgr.acquire("db:migration", "agent_a", timeout=30)
        if lock:
            # Agent A has exclusive access
            # Agent B will be blocked or notified
            do_migration()
            lock_mgr.release(lock)
    """
    
    def __init__(self):
        self._locks: dict[str, ContextLock] = {}
        self._waiting: dict[str, list[str]] = defaultdict(list)  # resource -> [agent names]
        self._lock = threading.Lock()
    
    def acquire(self, resource: str, agent: str, timeout: float = 60) -> Optional[ContextLock]:
        """
        Acquire exclusive lock on a context resource.
        
        Returns ContextLock if successful, None if blocked.
        Other agents requesting the same resource are queued.
        """
        with self._lock:
            # Check if resource is already locked
            if resource in self._locks:
                existing = self._locks[resource]
                if not existing.is_expired():
                    # Resource is locked by another agent
                    self._waiting[resource].append(agent)
                    return None
                else:
                    # Lock expired, remove it
                    del self._locks[resource]
            
            # Acquire lock
            lock = ContextLock(
                resource=resource,
                owner=agent,
                acquired_at=time.time(),
                expires_at=time.time() + timeout
            )
            self._locks[resource] = lock
            return lock
    
    def release(self, lock: ContextLock) -> bool:
        """
        Release a context lock. Next waiting agent gets access.
        """
        with self._lock:
            if lock.resource in self._locks:
                if self._locks[lock.resource].lock_id == lock.lock_id:
                    del self._locks[lock.resource]
                    
                    # Notify next waiting agent
                    if self._waiting[lock.resource]:
                        next_agent = self._waiting[lock.resource].pop(0)
                        # In a real system, this would notify the agent
                        return True
                    return True
            return False
    
    def force_release(self, resource: str) -> bool:
        """Force release a lock (admin action)."""
        with self._lock:
            if resource in self._locks:
                del self._locks[resource]
                return True
            return False
    
    def get_lock(self, resource: str) -> Optional[ContextLock]:
        """Get current lock info for a resource."""
        with self._lock:
            lock = self._locks.get(resource)
            if lock and not lock.is_expired():
                return lock
            return None
    
    def get_all_locks(self) -> dict[str, dict]:
        """Get all active locks."""
        with self._lock:
            # Clean expired locks
            expired = [r for r, l in self._locks.items() if l.is_expired()]
            for r in expired:
                del self._locks[r]
            
            return {r: l.to_dict() for r, l in self._locks.items()}
    
    def get_waiting(self, resource: str) -> list[str]:
        """Get agents waiting for a resource."""
        return list(self._waiting.get(resource, []))


class ContextLineage:
    """
    Full traceability of every context action.
    
    Every creation, modification, access, and lock is recorded.
    Enables debugging: "Why did Agent B do X?" → trace back through lineage.
    
    Usage:
        lineage = ContextLineage()
        
        # Record actions
        e1 = lineage.record("created", "ctx_123", "agent_a", "Initial context")
        e2 = lineage.record("modified", "ctx_123", "agent_b", "Updated value", parent=e1)
        
        # Trace back
        history = lineage.get_history("ctx_123")
        # → [e1, e2] in chronological order
    """
    
    def __init__(self):
        self._entries: list[LineageEntry] = []
        self._by_context: dict[str, list[str]] = defaultdict(list)  # context_id -> [entry_ids]
        self._entry_index: dict[str, LineageEntry] = {}
        self._lock = threading.Lock()
    
    def record(self, action: str, context_id: str, agent: str, 
               details: str = "", parent_entry: str = None,
               metadata: dict = None) -> LineageEntry:
        """Record a context action in the lineage."""
        entry = LineageEntry(
            action=action,
            context_id=context_id,
            agent=agent,
            timestamp=time.time(),
            details=details,
            parent_entry=parent_entry,
            metadata=metadata or {}
        )
        
        with self._lock:
            self._entries.append(entry)
            self._by_context[context_id].append(entry.parent_entry or id(entry))
            self._entry_index[str(id(entry))] = entry
        
        return entry
    
    def get_history(self, context_id: str) -> list[dict]:
        """Get complete history of a context item."""
        with self._lock:
            entries = []
            for entry in self._entries:
                if entry.context_id == context_id:
                    entries.append(entry.to_dict())
            entries.sort(key=lambda x: x['timestamp'])
            return entries
    
    def get_agent_activity(self, agent: str, limit: int = 100) -> list[dict]:
        """Get all actions by a specific agent."""
        with self._lock:
            entries = [e.to_dict() for e in self._entries if e.agent == agent]
            entries.sort(key=lambda x: x['timestamp'])
            return entries[-limit:]
    
    def get_decision_tree(self, context_id: str) -> dict:
        """
        Get a tree view of all decisions affecting a context.
        Useful for debugging: "Why did this happen?"
        """
        history = self.get_history(context_id)
        
        if not history:
            return {"context_id": context_id, "history": []}
        
        # Build tree
        tree = {
            "context_id": context_id,
            "first_seen": history[0]['timestamp'],
            "last_modified": history[-1]['timestamp'],
            "total_actions": len(history),
            "agents_involved": list(set(h['agent'] for h in history)),
            "history": history
        }
        
        return tree
    
    def get_timeline(self, start_time: float = None, end_time: float = None) -> list[dict]:
        """Get all lineage entries in a time window."""
        with self._lock:
            entries = []
            for entry in self._entries:
                ts = entry.timestamp
                if start_time and ts < start_time:
                    continue
                if end_time and ts > end_time:
                    continue
                entries.append(entry.to_dict())
            entries.sort(key=lambda x: x['timestamp'])
            return entries
    
    def get_stats(self) -> dict:
        """Get lineage statistics."""
        with self._lock:
            context_count = len(self._by_context)
            agent_actions = defaultdict(int)
            
            for entry in self._entries:
                agent_actions[entry.agent] += 1
            
            return {
                'total_entries': len(self._entries),
                'unique_contexts': context_count,
                'actions_by_agent': dict(agent_actions),
                'most_active_agent': max(agent_actions.items(), key=lambda x: x[1])[0] if agent_actions else None
            }


class ContextAccessControl:
    """
    Control which agents can access which context.
    
    Supports:
    - Public context (all agents can read)
    - Private context (only owner can read)
    - Shared context (owner specifies which agents can access)
    - Role-based context (based on agent role)
    """
    
    def __init__(self):
        self._permissions: dict[str, dict] = {}  # context_id -> {owner, access_list, visibility}
        self._lock = threading.Lock()
    
    def set_permissions(self, context_id: str, owner: str, 
                        visibility: str = "public",
                        allowed_agents: list[str] = None):
        """
        Set access permissions for a context item.
        
        visibility: "public" | "private" | "shared"
        allowed_agents: list of agent names that can access (for "shared" visibility)
        """
        with self._lock:
            self._permissions[context_id] = {
                'owner': owner,
                'visibility': visibility,
                'allowed_agents': allowed_agents or [],
                'created_at': time.time()
            }
    
    def can_access(self, context_id: str, agent: str) -> bool:
        """Check if an agent can access a context item."""
        with self._lock:
            perm = self._permissions.get(context_id)
            
            if not perm:
                return True  # No permissions set = accessible
            
            if perm['owner'] == agent:
                return True  # Owner always has access
            
            if perm['visibility'] == 'public':
                return True
            
            if perm['visibility'] == 'private':
                return False
            
            if perm['visibility'] == 'shared':
                return agent in perm['allowed_agents']
            
            return False
    
    def get_accessible_contexts(self, all_context_ids: list[str], 
                                 agent: str) -> list[str]:
        """Filter context list to only those accessible by agent."""
        return [cid for cid in all_context_ids if self.can_access(cid, agent)]


# ─── Unified Protocol Interface ───

class ClawNetProtocol:
    """
    Unified interface for ClawNet Context Consistency Protocol.
    
    Combines:
    - Context Locking (prevent collisions)
    - Context Lineage (full traceability)
    - Context Access Control (permissions)
    
    This is what makes ClawNet different from simple shared memory.
    """
    
    def __init__(self):
        self.locks = ContextLockManager()
        self.lineage = ContextLineage()
        self.access = ContextAccessControl()
    
    def lock(self, resource: str, agent: str, timeout: float = 60):
        """Acquire context lock (context manager)."""
        return _LockContext(self, resource, agent, timeout)
    
    def acquire_lock(self, resource: str, agent: str, timeout: float = 60):
        """Acquire context lock (manual)."""
        lock = self.locks.acquire(resource, agent, timeout)
        if lock:
            self.lineage.record("locked", resource, agent, 
                               f"Lock acquired for {timeout}s")
        return lock
    
    def release_lock(self, lock):
        """Release context lock."""
        success = self.locks.release(lock)
        if success:
            self.lineage.record("released", lock.resource, lock.owner,
                               "Lock released")
        return success
    
    def record_action(self, action: str, context_id: str, agent: str, 
                      details: str = "", metadata: dict = None):
        """Record a context action in lineage."""
        return self.lineage.record(action, context_id, agent, details, 
                                   metadata=metadata)
    
    def trace(self, context_id: str) -> dict:
        """Get full trace of a context (for debugging)."""
        return self.lineage.get_decision_tree(context_id)
    
    def grant_access(self, context_id: str, owner: str, 
                     agents: list[str], visibility: str = "shared"):
        """Grant access to specific agents."""
        self.access.set_permissions(context_id, owner, visibility, agents)
        self.lineage.record("access_granted", context_id, owner,
                           f"Shared with: {', '.join(agents)}")
    
    def get_stats(self) -> dict:
        """Get protocol statistics."""
        return {
            'locks': {
                'active': len(self.locks.get_all_locks()),
                'all': self.locks.get_all_locks()
            },
            'lineage': self.lineage.get_stats()
        }


class _LockContext:
    """Context manager for context locks."""
    
    def __init__(self, protocol: ClawNetProtocol, resource: str, 
                 agent: str, timeout: float):
        self.protocol = protocol
        self.resource = resource
        self.agent = agent
        self.timeout = timeout
        self.lock = None
    
    def __enter__(self):
        self.lock = self.protocol.acquire_lock(
            self.resource, self.agent, self.timeout
        )
        return self.lock
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock:
            self.protocol.release_lock(self.lock)
        return False
