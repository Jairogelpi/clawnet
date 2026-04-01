#!/usr/bin/env python3
"""
ClawNet Server — Shared Memory Bus for AI Agents

Runs on port 7890 (configurable). Stores agent memories,
provides semantic search, handles WebSocket sync.
"""

import asyncio
import json
import time
import math
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import hashlib

# ─── Embeddings: lightweight TF-IDF based (no ML dependency) ───

def tokenize(text: str) -> list[str]:
    text = text.lower()
    import re
    text = re.sub(r'[^\w\s]', ' ', text)
    stop = {'the','a','an','is','are','was','were','be','been','being','have','has',
            'had','do','does','did','will','would','could','should','may','might',
            'to','of','in','for','on','with','at','by','from','as','into','through',
            'i','me','my','we','our','you','your','he','him','his','she','her','it',
            'its','they','them','their','what','which','who','whom','and','also',
            'like','get','got','using','use','used','that','this','these','those'}
    return [t for t in text.split() if t not in stop and len(t) > 1]


def text_to_embedding(text: str, dim: int = 384) -> list[float]:
    """
    Generate a consistent embedding from text using hash-based approach.
    This is deterministic (same text → same embedding) and works offline.
    """
    tokens = tokenize(text)
    vec = [0.0] * dim
    
    for i, token in enumerate(tokens):
        # Hash each token to get a position in the embedding
        h = int(hashlib.md5(token.encode()).hexdigest()[:8], 16)
        pos = h % dim
        vec[pos] += 1.0 / (i + 1)  # Weight by position
        
        # Add bigrams if available
        if i > 0:
            bigram = tokens[i-1] + "_" + token
            h2 = int(hashlib.md5(bigram.encode()).hexdigest()[:8], 16)
            pos2 = h2 % dim
            vec[pos2] += 0.5 / (i + 1)
    
    # Normalize
    magnitude = math.sqrt(sum(x*x for x in vec))
    if magnitude > 0:
        vec = [x/magnitude for x in vec]
    
    return vec


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x*y for x,y in zip(a,b))
    mag_a = math.sqrt(sum(x*x for x in a))
    mag_b = math.sqrt(sum(x*x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ─── Data Models ───

@dataclass
class Memory:
    id: str
    agent: str
    content: str
    embedding: list[float]
    tags: list[str] = field(default_factory=list)
    emotion: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    strength: float = 1.0
    recall_count: int = 0

    def to_dict(self, include_embedding: bool = False) -> dict:
        d = {
            'id': self.id,
            'agent': self.agent,
            'content': self.content,
            'tags': self.tags,
            'emotion': self.emotion,
            'timestamp': self.timestamp,
            'strength': self.strength,
            'recall_count': self.recall_count
        }
        if include_embedding:
            d['embedding'] = [round(x, 4) for x in self.embedding]
        return d


@dataclass
class AgentInfo:
    name: str
    role: str
    connected_at: float
    last_seen: float
    memory_count: int = 0
    capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'role': self.role,
            'connected_at': self.connected_at,
            'last_seen': self.last_seen,
            'memory_count': self.memory_count,
            'capabilities': self.capabilities,
            'uptime_hours': round((time.time() - self.connected_at) / 3600, 2)
        }


# ─── Memory Store ───

class MemoryStore:
    def __init__(self, persist_path: Optional[str] = None):
        self.memories: dict[str, Memory] = {}
        self.agents: dict[str, AgentInfo] = {}
        self.persist_path = persist_path
        self._lock = threading.Lock()
        
        if persist_path:
            os.makedirs(persist_path, exist_ok=True)
            self._load()

    def add_memory(self, agent: str, content: str, tags: list[str] = None,
                   emotion: dict = None, memory_id: str = None) -> Memory:
        with self._lock:
            mem_id = memory_id or f"mem_{int(time.time()*1000)}_{agent}"
            embedding = text_to_embedding(content)
            
            mem = Memory(
                id=mem_id,
                agent=agent,
                content=content,
                embedding=embedding,
                tags=tags or [],
                emotion=emotion or {}
            )
            self.memories[mem_id] = mem
            
            # Update agent stats
            if agent in self.agents:
                self.agents[agent].memory_count += 1
                self.agents[agent].last_seen = time.time()
            
            if self.persist_path:
                self._save_memory(mem)
            
            return mem

    def query(self, text: str, limit: int = 10, min_score: float = 0.1,
              agent_filter: str = None, tag_filter: str = None) -> list[tuple[Memory, float]]:
        """Semantic search across all memories."""
        query_emb = text_to_embedding(text)
        results = []
        
        with self._lock:
            for mem in self.memories.values():
                if agent_filter and mem.agent != agent_filter:
                    continue
                if tag_filter and tag_filter not in mem.tags:
                    continue
                
                sim = cosine_similarity(query_emb, mem.embedding)
                
                # Boost by strength and recall count
                boosted = sim * mem.strength * (1 + 0.1 * mem.recall_count)
                
                if boosted >= min_score:
                    mem.recall_count += 1
                    results.append((mem, round(boosted, 4)))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def register_agent(self, name: str, role: str, capabilities: list[str] = None):
        with self._lock:
            self.agents[name] = AgentInfo(
                name=name,
                role=role,
                connected_at=time.time(),
                last_seen=time.time(),
                capabilities=capabilities or []
            )

    def get_agent_memories(self, agent: str, limit: int = 50) -> list[Memory]:
        with self._lock:
            mems = [m for m in self.memories.values() if m.agent == agent]
            mems.sort(key=lambda m: m.timestamp, reverse=True)
            return mems[:limit]

    def get_stats(self) -> dict:
        with self._lock:
            total_memories = len(self.memories)
            agents_count = len(self.agents)
            
            # Tag distribution
            tag_counts = defaultdict(int)
            for mem in self.memories.values():
                for tag in mem.tags:
                    tag_counts[tag] += 1
            
            # Agent distribution
            agent_counts = defaultdict(int)
            for mem in self.memories.values():
                agent_counts[mem.agent] += 1
            
            # Emotion averages
            emotion_sums = defaultdict(float)
            emotion_counts = defaultdict(int)
            for mem in self.memories.values():
                for k, v in mem.emotion.items():
                    emotion_sums[k] += v
                    emotion_counts[k] += 1
            
            emotion_avg = {k: round(emotion_sums[k]/emotion_counts[k], 3) 
                          for k in emotion_sums}
            
            return {
                'total_memories': total_memories,
                'total_agents': agents_count,
                'top_tags': dict(sorted(tag_counts.items(), key=lambda x: -x[1])[:20]),
                'memories_per_agent': dict(agent_counts),
                'emotion_averages': emotion_avg,
                'unique_tags': len(tag_counts)
            }

    def consolidate(self) -> dict:
        """
        Synaptic consolidation: find connections between memories,
        boost related ones, create new insights.
        """
        insights = []
        boosted = 0
        
        with self._lock:
            mems = list(self.memories.values())
            
            for i, mem_a in enumerate(mems):
                for mem_b in mems[i+1:]:
                    sim = cosine_similarity(mem_a.embedding, mem_b.embedding)
                    
                    # If memories are similar but from different agents,
                    # that's an interesting connection
                    if sim > 0.85 and mem_a.agent != mem_b.agent:
                        # Boost both memories (they reinforce each other)
                        mem_a.strength = min(mem_a.strength * 1.1, 3.0)
                        mem_b.strength = min(mem_b.strength * 1.1, 3.0)
                        boosted += 2
                        
                        insights.append({
                            'type': 'cross_agent_connection',
                            'memory_a': mem_a.id,
                            'memory_b': mem_b.id,
                            'agents': [mem_a.agent, mem_b.agent],
                            'similarity': round(sim, 4),
                            'summary': f"[{mem_a.agent}] and [{mem_b.agent}] learned similar things"
                        })
        
        return {
            'memories_boosted': boosted,
            'insights_found': len(insights),
            'insights': insights[:10]  # Top 10
        }

    def _save_memory(self, mem: Memory):
        if self.persist_path:
            path = os.path.join(self.persist_path, f"{mem.id}.json")
            with open(path, 'w') as f:
                json.dump(mem.to_dict(include_embedding=True), f)

    def _load(self):
        """Load persisted memories on startup."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return
        
        count = 0
        for fname in os.listdir(self.persist_path):
            if fname.endswith('.json'):
                path = os.path.join(self.persist_path, fname)
                try:
                    with open(path) as f:
                        data = json.load(f)
                    mem = Memory(
                        id=data['id'],
                        agent=data['agent'],
                        content=data['content'],
                        embedding=data.get('embedding', text_to_embedding(data['content'])),
                        tags=data.get('tags', []),
                        emotion=data.get('emotion', {}),
                        timestamp=data.get('timestamp', time.time()),
                        strength=data.get('strength', 1.0),
                        recall_count=data.get('recall_count', 0)
                    )
                    self.memories[mem.id] = mem
                    count += 1
                except Exception as e:
                    print(f"Error loading {fname}: {e}", file=sys.stderr)
        
        print(f"  Loaded {count} persisted memories", file=sys.stderr)


# ─── HTTP API ───

class ClawNetHandler(BaseHTTPRequestHandler):
    store: MemoryStore = None  # Set by main

    def log_message(self, format, *args):
        # Quieter logging
        pass

    def _send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _read_body(self) -> dict:
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/v1/agents':
            agents = [a.to_dict() for a in self.store.agents.values()]
            self._send_json({'agents': agents, 'count': len(agents)})
        
        elif path == '/v1/stats':
            self._send_json(self.store.get_stats())
        
        elif path.startswith('/v1/agents/') and path.endswith('/memories'):
            agent_name = path.split('/')[3]
            mems = self.store.get_agent_memories(agent_name)
            self._send_json({
                'agent': agent_name,
                'memories': [m.to_dict() for m in mems],
                'count': len(mems)
            })
        
        else:
            self._send_json({'error': 'not found', 'path': path}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            body = self._read_body()
        except Exception:
            self._send_json({'error': 'invalid JSON'}, 400)
            return
        
        if path == '/v1/memories':
            agent = body.get('agent', 'unknown')
            content = body.get('content', '')
            tags = body.get('tags', [])
            emotion = body.get('emotion', {})
            
            if not content:
                self._send_json({'error': 'content required'}, 400)
                return
            
            mem = self.store.add_memory(agent, content, tags, emotion)
            self._send_json({
                'id': mem.id,
                'status': 'created',
                'embedding_dim': len(mem.embedding)
            }, 201)
        
        elif path == '/v1/memories/query':
            text = body.get('text', '')
            limit = body.get('limit', 10)
            agent_filter = body.get('agent')
            tag_filter = body.get('tag')
            
            if not text:
                self._send_json({'error': 'text required'}, 400)
                return
            
            results = self.store.query(text, limit=limit,
                                        agent_filter=agent_filter,
                                        tag_filter=tag_filter)
            self._send_json({
                'query': text,
                'results': [
                    {
                        'memory': m.to_dict(),
                        'score': score
                    }
                    for m, score in results
                ],
                'count': len(results)
            })
        
        elif path == '/v1/agents/register':
            name = body.get('name')
            role = body.get('role', 'agent')
            capabilities = body.get('capabilities', [])
            
            if not name:
                self._send_json({'error': 'name required'}, 400)
                return
            
            self.store.register_agent(name, role, capabilities)
            self._send_json({'status': 'registered', 'agent': name})
        
        elif path == '/v1/consolidate':
            result = self.store.consolidate()
            self._send_json(result)
        
        else:
            self._send_json({'error': 'not found', 'path': path}, 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def run_server(host: str = '0.0.0.0', port: int = 7890, 
               persist_path: Optional[str] = None):
    """Start the ClawNet memory server."""
    store = MemoryStore(persist_path)
    
    # Inject store into handler
    ClawNetHandler.store = store
    
    server = HTTPServer((host, port), ClawNetHandler)
    
    print(f"""
╔════════════════════════════════════════════════╗
║  🧠 ClawNet Memory Server                      ║
║  Listening on {host}:{port}                    ║
║  Persist: {persist_path or 'memory only'}      ║
║  Protocol: v1.0                                ║
╚════════════════════════════════════════════════╝
    
Endpoints:
  GET  /v1/agents          — List connected agents
  GET  /v1/stats           — Server statistics
  POST /v1/memories        — Publish memory
  POST /v1/memories/query  — Semantic search
  POST /v1/agents/register — Register agent
  POST /v1/consolidate     — Run consolidation
  
Quick test:
  curl http://localhost:{port}/v1/stats
""")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down ClawNet...")
        server.shutdown()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='ClawNet Memory Server')
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=7890)
    parser.add_argument('--persist', default='./clawnet-data')
    args = parser.parse_args()
    
    run_server(args.host, args.port, args.persist)
