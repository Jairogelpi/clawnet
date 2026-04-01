# 🧠 ClawNet — Distributed Agent Consciousness Protocol

**The nervous system for AI agents. Not messaging — shared memory, collective learning, emergent capabilities.**

```
    ┌─────────────────────────────────────────────────────────┐
    │                    SHARED SYNAPTIC BUS                  │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
    │  │ Mem v5   │  │ Docs     │  │ Learning │  Collective  │
    │  │Embeddings│  │ Knowledge│  │ Patterns │   Memory     │
    │  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
    │       │             │             │                     │
    │  ┌────┴─────────────┴─────────────┴────┐               │
    │  │        SHARED MEMORY LAYER          │               │
    │  │   (synced embeddings + experiences) │               │
    │  └─────────────────┬───────────────────┘               │
    │                    │                                    │
    │    ┌───────────────┼───────────────┐                   │
    │    ▼               ▼               ▼                   │
    │ ┌──────┐      ┌──────────┐    ┌────────┐              │
    │ │Open- │      │  Hermes  │    │  n8n   │              │
    │ │Claw  │      │   CLI    │    │Workflows│              │
    │ └──────┘      └──────────┘    └────────┘              │
    │  Agent A        Agent B        Agent C                 │
    └─────────────────────────────────────────────────────────┘
```

## The Problem

Today's agent protocols (MCP, A2A) are like **email between agents**. They pass messages. Nothing more.

When OpenClaw learns something, Hermes doesn't know. When Paperclip processes a document, it doesn't feed back to the system. Agents are isolated islands that occasionally exchange messages.

**This is like having email but no nervous system.**

## The Solution: ClawNet

ClawNet creates a **shared memory layer** for AI agents. Not messaging — **collective consciousness**.

### What Makes This Different

| Existing (MCP/A2A) | ClawNet |
|-------------------|---------|
| Agent ↔ Agent messaging | Agent ↔ Shared Memory ↔ Agent |
| Each agent isolated | All agents share experiences |
| No collective learning | Experiences feed back to all |
| Point-to-point | Distributed synaptic bus |

### The Analogy

- **TCP/IP** connected networks → created the Internet
- **A2A** connects agents → creates... better messaging
- **ClawNet** connects agent minds → creates **collective consciousness**

## How It Works

### 1. Shared Synaptic Bus

Every agent publishes its experiences as 384-dim embeddings. Other agents can query, retrieve, and learn from them.

```python
# Agent A learns something
clawnet.publish(
    memory="New pattern: user prefers Spanish responses",
    tags=["preference", "language"],
    emotional_weight=0.8
)

# Agent B (running elsewhere) automatically benefits
insights = clawnet.query("user preferences", top_k=5)
# Returns Agent A's learning, even though B never experienced it
```

### 2. Collective Dream Cycles

Like how your brain consolidates memories during sleep, ClawNet runs periodic **synaptic consolidation** — finding connections between agents' experiences and creating new insights.

```python
# Runs automatically every 30 minutes
# Finds patterns across ALL connected agents
clawnet.consolidate()
# → New emergent insight: "User values honesty over accuracy when stakes are high"
```

### 3. Capability Negotiation

Agents discover what others can do and delegate intelligently.

```python
# "I need code review — who's good at this?"
best_agent = clawnet.find_capability("code_review", min_score=0.8)
result = clawnet.delegate(best_agent, "review this PR", context)
```

## Quick Start

### Install

```bash
pip install clawnet
```

### Run the Memory Server

```bash
# Start the shared memory server (runs on port 7890)
clawnet-server --port 7890 --persist ./clawnet-data
```

### Connect Your Agents

```python
from clawnet import AgentClient

# Connect OpenClaw
agent = AgentClient(
    name="cobos",
    role="orchestrator",
    server="localhost:7890"
)

# Publish a memory
agent.remember(
    content="Jairo prefers direct communication, no fluff",
    tags=["jairo", "preference", "communication"],
    emotion={"trust": 0.9, "energy": 0.7}
)

# Query shared memories (from ANY connected agent)
memories = agent.recall("what do we know about Jairo?", limit=10)

# Check what other agents know
agents = agent.list_agents()
for a in agents:
    print(f"{a.name}: {a.memory_count} memories, focus: {a.top_tags}")
```

### Connect Multiple Agents

```python
# Hermes agent — same server, different identity
hermes = AgentClient(
    name="hermes",
    role="researcher",
    server="localhost:7890"
)

# Hermes can access Cobos's memories automatically
jairo_prefs = hermes.recall("Jairo preferences")
# Returns memories that Cobos published — shared consciousness
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ClawNet Protocol v1                      │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: EMERGENCE                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Synaptic     │  │ Capability   │  │ Collective       │  │
│  │ Consolidation│  │ Negotiation  │  │ Dream Cycles     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: MEMORY                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 384-dim      │  │ Experience   │  │ Associative      │  │
│  │ Embeddings   │  │ Graph        │  │ Recall           │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: TRANSPORT                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ WebSocket    │  │ Capability   │  │ Auth &           │  │
│  │ Sync         │  │ Discovery    │  │ Encryption       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Protocol Specification

### Memory Format

```json
{
  "id": "mem_abc123",
  "agent": "cobos",
  "content": "User prefers direct communication",
  "embedding": [0.12, -0.34, 0.56, ...],
  "tags": ["preference", "communication"],
  "emotion": {"trust": 0.9, "energy": 0.7},
  "timestamp": "2026-04-01T19:30:00Z",
  "strength": 1.5,
  "recall_count": 3
}
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/memories` | Publish a new memory |
| `POST` | `/v1/memories/query` | Semantic search across all memories |
| `GET` | `/v1/agents` | List connected agents |
| `GET` | `/v1/agents/{id}/memories` | Get memories from specific agent |
| `POST` | `/v1/consolidate` | Trigger synaptic consolidation |
| `GET` | `/v1/capabilities` | List agent capabilities |
| `WS` | `/v1/sync` | Real-time WebSocket sync |

## Use Cases

### 1. Multi-Agent Teams
OpenClaw orchestrates, Hermes researches, Paperclip manages docs — all share the same memory pool.

### 2. Personal AI Network
Your laptop agent, your phone agent, your server agent — all share your life's context.

### 3. Team Collaboration
Multiple developers' agents share project knowledge without sharing private data.

### 4. Agent Evolution
Agents learn from each other's successes and failures, improving collectively.

## What This Enables That Nothing Else Does

1. **Cross-agent memory transfer** — Agent A's experience benefits Agent B
2. **Collective intelligence** — The network is smarter than any individual agent
3. **Emergent capabilities** — Patterns no single agent could detect alone
4. **Agent evolution** — The system improves as agents learn from each other

## Status

🚧 **Active Development** — MVP working, protocol v1 stable

### Roadmap

- [x] Protocol specification v1
- [x] Memory server with semantic search
- [x] Python client SDK
- [ ] WebSocket real-time sync
- [ ] Node.js client SDK
- [ ] Docker deployment
- [ ] Encrypted memory channels
- [ ] Capability marketplace
- [ ] Agent reputation system

## Contributing

ClawNet is open source. The protocol is agent-agnostic — any AI agent can connect.

```bash
git clone https://github.com/cobosnet/clawnet.git
cd clawnet
pip install -e .
```

## License

MIT — use it, build on it, make it yours.

---

**ClawNet** — Because agents shouldn't be alone.
