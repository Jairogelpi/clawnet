#!/usr/bin/env python3
"""
ClawNet Client — Connect any AI agent to the shared memory bus.

Usage:
    from clawnet.client import ClawNetClient
    
    agent = ClawNetClient("my-agent", "researcher", server="localhost:7890")
    agent.remember("User likes direct communication", tags=["preference"])
    memories = agent.recall("what do we know about the user?")
"""

import json
import time
import urllib.request
import urllib.error
from typing import Optional


class ClawNetClient:
    """Client for connecting to ClawNet shared memory."""
    
    def __init__(self, name: str, role: str = "agent",
                 server: str = "localhost:7890",
                 capabilities: list[str] = None):
        self.name = name
        self.role = role
        self.server = server if server.startswith("http") else f"http://{server}"
        self.capabilities = capabilities or []
        
        # Register on connect
        self._register()
    
    def _request(self, method: str, path: str, data: dict = None) -> dict:
        url = f"{self.server}{path}"
        headers = {'Content-Type': 'application/json'}
        
        body = json.dumps(data or {}).encode() if data else None
        
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            return {'error': f"HTTP {e.code}", 'detail': error_body}
        except urllib.error.URLError as e:
            return {'error': 'connection_failed', 'detail': str(e.reason)}
    
    def _register(self):
        """Register this agent with the server."""
        result = self._request('POST', '/v1/agents/register', {
            'name': self.name,
            'role': self.role,
            'capabilities': self.capabilities
        })
        if 'error' in result:
            print(f"ClawNet: Warning - could not register: {result['error']}")
    
    def remember(self, content: str, tags: list[str] = None,
                 emotion: dict = None) -> dict:
        """Publish a memory to the shared bus."""
        result = self._request('POST', '/v1/memories', {
            'agent': self.name,
            'content': content,
            'tags': tags or [],
            'emotion': emotion or {}
        })
        return result
    
    def recall(self, query: str, limit: int = 10, 
               agent: str = None, tag: str = None) -> list[dict]:
        """Semantic search across ALL connected agents' memories."""
        data = {
            'text': query,
            'limit': limit
        }
        if agent:
            data['agent'] = agent
        if tag:
            data['tag'] = tag
        
        result = self._request('POST', '/v1/memories/query', data)
        
        if 'results' in result:
            return result['results']
        return []
    
    def list_agents(self) -> list[dict]:
        """List all connected agents."""
        result = self._request('GET', '/v1/agents')
        return result.get('agents', [])
    
    def get_stats(self) -> dict:
        """Get server statistics."""
        return self._request('GET', '/v1/stats')
    
    def consolidate(self) -> dict:
        """Trigger synaptic consolidation across all memories."""
        return self._request('POST', '/v1/consolidate')
    
    def get_my_memories(self, limit: int = 50) -> list[dict]:
        """Get all memories from this agent."""
        result = self._request('GET', f'/v1/agents/{self.name}/memories')
        return result.get('memories', [])
    
    # ─── Convenience methods ───
    
    def remember_preference(self, user: str, preference: str, 
                            importance: float = 0.8):
        """Shortcut for storing user preferences."""
        return self.remember(
            content=f"User {user} prefers: {preference}",
            tags=["preference", user.lower().replace(" ", "_")],
            emotion={"trust": importance}
        )
    
    def remember_insight(self, insight: str, source: str = "observation"):
        """Shortcut for storing insights."""
        return self.remember(
            content=insight,
            tags=["insight", source],
            emotion={"curiosity": 0.7}
        )
    
    def find_similar(self, content: str, threshold: float = 0.8) -> list[dict]:
        """Find memories similar to given content."""
        results = self.recall(content, limit=20)
        return [r for r in results if r.get('score', 0) >= threshold]
    
    def search_by_tag(self, tag: str, limit: int = 20) -> list[dict]:
        """Get all memories with a specific tag."""
        result = self._request('POST', '/v1/memories/query', {
            'text': tag,
            'limit': limit,
            'tag': tag
        })
        return result.get('results', [])


class ClawNetBridge:
    """
    Bridge for integrating ClawNet with existing systems.
    Provides hooks for OpenClaw, Hermes, and custom agents.
    """
    
    def __init__(self, client: ClawNetClient):
        self.client = client
        self._hooks = {}
    
    def on_memory(self, callback):
        """Register callback for when new memories arrive."""
        self._hooks['memory'] = callback
        return callback
    
    def auto_capture(self, content: str, context: dict = None,
                     tags: list[str] = None):
        """
        Auto-capture pattern: intelligently stores important information.
        Use this as a hook for agent events.
        """
        important_tags = list(tags or [])
        
        # Auto-detect type
        if any(word in content.lower() for word in ['prefer', 'like', 'hate', 'want']):
            important_tags.append('preference')
        if any(word in content.lower() for word in ['learned', 'realized', 'discovered']):
            important_tags.append('insight')
        if any(word in content.lower() for word in ['error', 'bug', 'broken', 'failed']):
            important_tags.append('issue')
        
        emotion = {}
        if context:
            if 'trust' in context:
                emotion['trust'] = context['trust']
            if 'energy' in context:
                emotion['energy'] = context['energy']
        
        return self.client.remember(content, tags=important_tags, emotion=emotion)
    
    def get_context_for(self, topic: str, max_memories: int = 5) -> str:
        """
        Get formatted context string for injecting into prompts.
        Useful for giving an LLM access to shared memories.
        """
        results = self.client.recall(topic, limit=max_memories)
        
        if not results:
            return ""
        
        lines = ["[Shared Memory Context]"]
        for r in results:
            mem = r.get('memory', {})
            score = r.get('score', 0)
            agent = mem.get('agent', 'unknown')
            content = mem.get('content', '')
            lines.append(f"- [{agent}] {content} (relevance: {score:.0%})")
        
        return "\n".join(lines)
