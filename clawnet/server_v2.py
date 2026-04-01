#!/usr/bin/env python3
"""
ClawNet Server v2 — Context Consistency with WebSocket real-time sync

Adds to v1:
- WebSocket server for real-time context sync between agents
- Context Locking API
- Context Lineage API  
- Context Access Control API
- MCP-compatible endpoints
"""

import asyncio
import json
import time
import math
import os
import sys
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional
from http.server import HTTPServer
import threading
import re

from .server import MemoryStore, Memory, AgentInfo, ClawNetHandler, text_to_embedding, cosine_similarity
from .protocol import ClawNetProtocol, ContextLockManager, ContextLineage, ContextAccessControl


# ─── WebSocket Server (simplified, no external deps) ───

class WebSocketFrame:
    """Minimal WebSocket frame parser (RFC 6455)."""
    
    @staticmethod
    def decode(data: bytes) -> Optional[str]:
        if len(data) < 2:
            return None
        
        opcode = data[0] & 0x0F
        masked = (data[1] & 0x80) != 0
        payload_len = data[1] & 0x7F
        
        if payload_len == 126:
            if len(data) < 4:
                return None
            payload_len = int.from_bytes(data[2:4], 'big')
            mask_start = 4
        elif payload_len == 127:
            if len(data) < 10:
                return None
            payload_len = int.from_bytes(data[2:10], 'big')
            mask_start = 10
        else:
            mask_start = 2
        
        if masked:
            if len(data) < mask_start + 4 + payload_len:
                return None
            mask = data[mask_start:mask_start+4]
            payload = data[mask_start+4:mask_start+4+payload_len]
            decoded = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        else:
            if len(data) < mask_start + payload_len:
                return None
            decoded = data[mask_start:mask_start+payload_len]
        
        if opcode == 0x1:  # Text frame
            return decoded.decode('utf-8', errors='replace')
        elif opcode == 0x8:  # Close
            return None
        return ""
    
    @staticmethod
    def encode(data: str) -> bytes:
        payload = data.encode('utf-8')
        frame = bytearray()
        frame.append(0x81)  # FIN + text frame
        length = len(payload)
        if length < 126:
            frame.append(length)
        elif length < 65536:
            frame.append(126)
            frame.extend(length.to_bytes(2, 'big'))
        else:
            frame.append(127)
            frame.extend(length.to_bytes(8, 'big'))
        frame.extend(payload)
        return bytes(frame)


class ClawNetServerV2:
    """
    ClawNet v2 Server — HTTP REST + WebSocket + Context Consistency
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 7890,
                 persist_path: str = None):
        self.host = host
        self.port = port
        self.store = MemoryStore(persist_path)
        self.protocol = ClawNetProtocol()
        self.ws_clients: dict[str, list] = defaultdict(list)  # topic -> [websocket connections]
        
        # Inject into HTTP handler
        ClawNetHandler.store = self.store
        
        # Track protocol for HTTP endpoints
        self._protocol = self.protocol
    
    def handle_http(self, method: str, path: str, body: dict = None) -> tuple[dict, int]:
        """Route HTTP requests to handlers."""
        body = body or {}
        
        # ─── Existing Memory API (v1) ───
        if path == '/v1/memories' and method == 'POST':
            agent = body.get('agent', 'unknown')
            content = body.get('content', '')
            tags = body.get('tags', [])
            emotion = body.get('emotion', {})
            
            if not content:
                return {'error': 'content required'}, 400
            
            mem = self.store.add_memory(agent, content, tags, emotion)
            self.protocol.record_action("created", mem.id, agent, 
                                       f"Memory: {content[:50]}...")
            
            # Broadcast to WebSocket subscribers
            self._broadcast('new_memory', {
                'id': mem.id, 'agent': agent, 
                'content': content[:100], 'tags': tags
            })
            
            return {'id': mem.id, 'status': 'created'}, 201
        
        elif path == '/v1/memories/query' and method == 'POST':
            text = body.get('text', '')
            limit = body.get('limit', 10)
            
            if not text:
                return {'error': 'text required'}, 400
            
            results = self.store.query(text, limit=limit)
            return {
                'query': text,
                'results': [
                    {'memory': m.to_dict(), 'score': score}
                    for m, score in results
                ]
            }, 200
        
        elif path == '/v1/stats' and method == 'GET':
            stats = self.store.get_stats()
            stats['protocol'] = self.protocol.get_stats()
            return stats, 200
        
        # ─── Context Locking API (v2) ───
        elif path == '/v2/locks' and method == 'POST':
            resource = body.get('resource')
            agent = body.get('agent')
            timeout = body.get('timeout', 60)
            
            if not resource or not agent:
                return {'error': 'resource and agent required'}, 400
            
            lock = self.protocol.acquire_lock(resource, agent, timeout)
            if lock:
                self._broadcast('lock_acquired', lock.to_dict())
                return lock.to_dict(), 201
            else:
                waiting = self.protocol.locks.get_waiting(resource)
                return {
                    'error': 'resource_locked',
                    'waiting': waiting
                }, 409
        
        elif path == '/v2/locks/release' and method == 'POST':
            resource = body.get('resource')
            agent = body.get('agent')
            
            if not resource:
                return {'error': 'resource required'}, 400
            
            # Find and release lock
            lock = self.protocol.locks.get_lock(resource)
            if lock and lock.owner == agent:
                self.protocol.release_lock(lock)
                self._broadcast('lock_released', {'resource': resource})
                return {'status': 'released'}, 200
            elif lock:
                return {'error': 'not_lock_owner'}, 403
            else:
                return {'error': 'no_lock_found'}, 404
        
        elif path == '/v2/locks' and method == 'GET':
            locks = self.protocol.locks.get_all_locks()
            return {'locks': locks, 'count': len(locks)}, 200
        
        # ─── Context Lineage API (v2) ───
        elif path == '/v2/lineage' and method == 'POST':
            context_id = body.get('context_id')
            if not context_id:
                return {'error': 'context_id required'}, 400
            
            history = self.protocol.lineage.get_history(context_id)
            tree = self.protocol.lineage.get_decision_tree(context_id)
            return tree, 200
        
        elif path == '/v2/lineage/agent' and method == 'POST':
            agent = body.get('agent')
            if not agent:
                return {'error': 'agent required'}, 400
            
            activity = self.protocol.lineage.get_agent_activity(agent)
            return {'agent': agent, 'activity': activity, 'count': len(activity)}, 200
        
        elif path == '/v2/lineage/timeline' and method == 'POST':
            start = body.get('start_time')
            end = body.get('end_time')
            timeline = self.protocol.lineage.get_timeline(start, end)
            return {'timeline': timeline, 'count': len(timeline)}, 200
        
        # ─── Context Access Control API (v2) ───
        elif path == '/v2/access/grant' and method == 'POST':
            context_id = body.get('context_id')
            owner = body.get('owner')
            agents = body.get('agents', [])
            visibility = body.get('visibility', 'shared')
            
            if not context_id or not owner:
                return {'error': 'context_id and owner required'}, 400
            
            self.protocol.grant_access(context_id, owner, agents, visibility)
            return {'status': 'granted', 'agents': agents}, 200
        
        elif path == '/v2/access/check' and method == 'POST':
            context_id = body.get('context_id')
            agent = body.get('agent')
            
            can_access = self.protocol.access.can_access(context_id, agent)
            return {'context_id': context_id, 'agent': agent, 
                    'can_access': can_access}, 200
        
        # ─── Consolidation (v1) ───
        elif path == '/v1/consolidate' and method == 'POST':
            result = self.store.consolidate()
            return result, 200
        
        # ─── Agents API ───
        elif path == '/v1/agents' and method == 'GET':
            agents = [a.to_dict() for a in self.store.agents.values()]
            return {'agents': agents, 'count': len(agents)}, 200
        
        elif path == '/v1/agents/register' and method == 'POST':
            name = body.get('name')
            role = body.get('role', 'agent')
            capabilities = body.get('capabilities', [])
            
            if not name:
                return {'error': 'name required'}, 400
            
            self.store.register_agent(name, role, capabilities)
            self.protocol.record_action("agent_joined", "system", name,
                                       f"Role: {role}")
            self._broadcast('agent_joined', {'name': name, 'role': role})
            return {'status': 'registered', 'agent': name}, 201
        
        # ─── MCP Compatibility (v2) ───
        elif path == '/mcp/tools' and method == 'GET':
            # MCP-compatible tool list
            tools = [
                {
                    "name": "clawnet_remember",
                    "description": "Store a memory in the shared context",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "tags": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["content"]
                    }
                },
                {
                    "name": "clawnet_recall", 
                    "description": "Query shared context memories",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "limit": {"type": "integer"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "clawnet_lock",
                    "description": "Acquire context lock to prevent collisions",
                    "inputSchema": {
                        "type": "object", 
                        "properties": {
                            "resource": {"type": "string"},
                            "timeout": {"type": "integer"}
                        },
                        "required": ["resource"]
                    }
                }
            ]
            return {'tools': tools}, 200
        
        else:
            return {'error': 'not found', 'path': path}, 404
    
    def _broadcast(self, event_type: str, data: dict):
        """Broadcast event to all WebSocket subscribers."""
        message = json.dumps({
            'event': event_type,
            'data': data,
            'timestamp': time.time()
        })
        
        for topic_clients in self.ws_clients.values():
            for ws in topic_clients[:]:
                try:
                    ws.send(WebSocketFrame.encode(message))
                except:
                    topic_clients.remove(ws)
    
    def run(self):
        """Start the server (HTTP + WebSocket)."""
        import socket
        
        # Custom socket server that handles HTTP + WebSocket upgrade
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(50)
        server_socket.settimeout(1.0)
        
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  🧠 ClawNet v2 — Context Consistency Protocol                   ║
║  Listening on {self.host}:{self.port}                              ║
║  HTTP REST + WebSocket + Context Locking + Lineage               ║
╠══════════════════════════════════════════════════════════════════╣
║  v1 API:                                                         ║
║    POST /v1/memories          — Store memory                     ║
║    POST /v1/memories/query    — Semantic search                  ║
║    GET  /v1/agents            — List agents                      ║
║    POST /v1/consolidate       — Run consolidation                ║
║                                                                   ║
║  v2 API (Context Consistency):                                    ║
║    POST /v2/locks             — Acquire context lock             ║
║    POST /v2/locks/release     — Release lock                     ║
║    GET  /v2/locks             — List active locks                ║
║    POST /v2/lineage           — Get context history              ║
║    POST /v2/lineage/agent     — Get agent activity               ║
║    POST /v2/access/grant      — Grant context access             ║
║    POST /v2/access/check      — Check access permissions         ║
║                                                                   ║
║  MCP Compatible:                                                  ║
║    GET  /mcp/tools            — MCP tool definitions             ║
║                                                                   ║
║  WebSocket: ws://localhost:{self.port}/ws                          ║
╚══════════════════════════════════════════════════════════════════╝
""")
        
        while True:
            try:
                client_socket, addr = server_socket.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr),
                    daemon=True
                ).start()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                print("\n  Shutting down ClawNet v2...")
                break
    
    def _handle_client(self, client_socket, addr):
        """Handle HTTP or WebSocket client."""
        try:
            data = client_socket.recv(4096)
            if not data:
                client_socket.close()
                return
            
            request = data.decode('utf-8', errors='replace')
            first_line = request.split('\r\n')[0] if '\r\n' in request else request.split('\n')[0]
            
            # Check for WebSocket upgrade
            if 'Upgrade: websocket' in request.lower():
                self._handle_websocket(client_socket, request)
                return
            
            # Parse HTTP request
            parts = first_line.split(' ')
            method = parts[0] if len(parts) > 0 else 'GET'
            path = parts[1] if len(parts) > 1 else '/'
            
            # Parse body
            body = {}
            if '\r\n\r\n' in request:
                body_str = request.split('\r\n\r\n', 1)[1]
                try:
                    body = json.loads(body_str)
                except:
                    pass
            
            # Handle request
            response_data, status = self.handle_http(method, path, body)
            
            # Send response
            status_text = {200: 'OK', 201: 'Created', 400: 'Bad Request',
                          403: 'Forbidden', 404: 'Not Found', 409: 'Conflict'}.get(status, 'OK')
            
            response = json.dumps(response_data, ensure_ascii=False)
            response_bytes = (
                f"HTTP/1.1 {status} {status_text}\r\n"
                f"Content-Type: application/json\r\n"
                f"Access-Control-Allow-Origin: *\r\n"
                f"Content-Length: {len(response.encode())}\r\n"
                f"\r\n{response}"
            ).encode()
            
            client_socket.sendall(response_bytes)
            
        except Exception as e:
            error_response = json.dumps({'error': str(e)})
            client_socket.sendall(
                f"HTTP/1.1 500 Internal Server Error\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(error_response.encode())}\r\n"
                f"\r\n{error_response}".encode()
            )
        finally:
            client_socket.close()
    
    def _handle_websocket(self, client_socket, request):
        """Handle WebSocket connection."""
        import base64
        
        # Extract WebSocket key
        ws_key = None
        for line in request.split('\r\n'):
            if line.lower().startswith('sec-websocket-key:'):
                ws_key = line.split(':', 1)[1].strip()
                break
        
        if not ws_key:
            client_socket.close()
            return
        
        # Generate accept key
        import hashlib
        magic = "258EAFA5-E914-47DA-95CA-5AB0DC85B727"
        accept = base64.b64encode(
            hashlib.sha1((ws_key + magic).encode()).digest()
        ).decode()
        
        # Send handshake
        handshake = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept}\r\n"
            "\r\n"
        ).encode()
        client_socket.sendall(handshake)
        
        # Subscribe to all events
        topic = "all"
        self.ws_clients[topic].append(client_socket)
        
        # Send welcome message
        welcome = json.dumps({
            'event': 'connected',
            'data': {'topic': topic, 'server': 'clawnet-v2'},
            'timestamp': time.time()
        })
        client_socket.sendall(WebSocketFrame.encode(welcome))
        
        # Listen for messages
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                message = WebSocketFrame.decode(data)
                if message:
                    try:
                        msg = json.loads(message)
                        # Handle subscriptions
                        if msg.get('action') == 'subscribe':
                            topic = msg.get('topic', 'all')
                            self.ws_clients[topic].append(client_socket)
                    except:
                        pass
        except:
            pass
        finally:
            # Remove from clients
            for topic_clients in self.ws_clients.values():
                if client_socket in topic_clients:
                    topic_clients.remove(client_socket)
            client_socket.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='ClawNet v2 Context Consistency Server')
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=7890)
    parser.add_argument('--persist', default='./clawnet-data')
    args = parser.parse_args()
    
    server = ClawNetServerV2(args.host, args.port, args.persist)
    server.run()


if __name__ == '__main__':
    main()
