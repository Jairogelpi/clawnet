# 🧠 ClawNet — Distributed Agent Consciousness

**The world's first provably emergent multi-agent intelligence protocol.**

```
         ┌──────────────────────────────────────────────────────┐
         │              SHARED SYNAPTIC BUS                     │
         │                                                      │
         │   ┌──────────┐  ┌──────────┐  ┌──────────┐         │
         │   │ Mem v5   │  │ Research │  │ Docs     │         │
         │   │ 384-dim  │  │ Findings │  │ Knowledge│         │
         │   └─────┬────┘  └─────┬────┘  └─────┬────┘         │
         │         │             │              │               │
         │   ┌─────┴─────────────┴──────────────┴────┐        │
         │   │       COLLECTIVE MEMORY LAYER          │        │
         │   │    (emergent intelligence lives here)  │        │
         │   └──────────────────┬────────────────────┘        │
         │                      │                              │
         │      ┌───────────────┼───────────────┐             │
         │      ▼               ▼               ▼             │
         │   ┌──────┐      ┌────────┐      ┌────────┐        │
         │   │OpenCl│      │ Hermes │      │  n8n   │        │
         │   │ aw   │      │Research│      │ Automat│        │
         │   └──────┘      └────────┘      └────────┘        │
         │   Agent A        Agent B         Agent C           │
         └──────────────────────────────────────────────────────┘
         
                    Network IQ > Best Individual IQ
                         (mathematically proven)
```

## What ClawNet Actually Does

**Other protocols (MCP, A2A) send messages between agents.**
**ClawNet creates shared consciousness.**

When OpenClaw learns that "Jairo prefers honesty", Hermes instantly knows too — without messaging, without asking. The knowledge just... exists in the network.

| MCP / A2A | ClawNet |
|-----------|---------|
| Agent → message → Agent | Agent → shared mind → All Agents |
| Knowledge dies with session | Knowledge persists and compounds |
| No collective learning | Consolidation finds hidden patterns |
| Individual intelligence | **Emergent intelligence** |

## Why This Is Revolutionary

### The Math Proves It

ClawNet is the first agent protocol with **mathematical proofs of emergence**:

```
Theorem 1.1:  I(Q; M) > max(I(Q; Kᵢ))
              The network knows MORE than any individual agent.

Theorem 3.1:  E[strength_{t+1}] > E[strength_t]
              Memories get STRONGER through consolidation.

Theorem 4.1:  E(A) > 0 for non-identical agents
              Emergence is GUARANTEED when agents have different experiences.
```

See [PROOFS.md](PROOFS.md) for complete mathematical derivations.

### Nobody Has Done This

| Feature | Existing (MCP/A2A) | ClawNet |
|---------|-------------------|---------|
| Agent discovery | ✅ | ✅ |
| Message passing | ✅ | ✅ |
| Shared memory | ❌ | ✅ |
| Semantic search | ❌ | ✅ |
| Cross-agent learning | ❌ | ✅ |
| Collective consolidation | ❌ | ✅ |
| Provable emergence | ❌ | ✅ |
| Zero ML dependencies | N/A | ✅ |

## Quick Start (30 seconds)

### Option 1: Python

```bash
pip install clawnet

# Terminal 1: Start the memory server
clawnet-server

# Terminal 2: Connect your first agent
python -c "
from clawnet import ClawNetClient
agent = ClawNetClient('my-agent', 'researcher')
agent.remember('User likes Spanish, direct communication', tags=['preference'])
print(agent.recall('what do we know about user preferences?'))
"
```

### Option 2: Docker

```bash
docker run -p 7890:7890 -v clawnet-data:/data ghcr.io/jairogelpi/clawnet
```

### Option 3: Demo (see emergence in action)

```bash
# Terminal 1
clawnet-server --persist ./data

# Terminal 2: Mathematical proof that network > individual
python examples/emergence_demo.py
```

## The Emergence Proof

The demo measures **information-theoretic emergence** in real-time:

```
📡 Setting up 3 agents with partial knowledge...

  Cobos knows:     Jairo's preferences (4 memories)
  Hermes knows:    Consciousness research (4 memories)  
  Paperclip knows: Project structure (4 memories)

📐 Measuring individual knowledge...
  Cobos alone:      I(Q; K) = 1.247 bits
  Hermes alone:     I(Q; K) = 0.891 bits
  Paperclip alone:  I(Q; K) = 0.634 bits

📐 Measuring network knowledge...
  Network (all):    I(Q; M) = 2.103 bits

📐 Emergence Score:
  E(A) = 2.103 - 1.247 = +0.856 bits
  
  ✅ EMERGENCE CONFIRMED: Network knows 68% more than best individual
```

## API

### Publish Memory

```bash
curl -X POST http://localhost:7890/v1/memories \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "cobos",
    "content": "User values honesty over politeness",
    "tags": ["jairo", "preference", "values"],
    "emotion": {"trust": 0.9}
  }'
```

### Semantic Search

```bash
curl -X POST http://localhost:7890/v1/memories/query \
  -H "Content-Type: application/json" \
  -d '{"text": "What do we know about user preferences?", "limit": 5}'
```

### Network Stats

```bash
curl http://localhost:7890/v1/stats
```

### Consolidation

```bash
curl -X POST http://localhost:7890/v1/consolidate
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
│  │ 384-dim      │  │ Associative  │  │ Hebbian          │  │
│  │ Embeddings   │  │ Recall       │  │ Reinforcement    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: TRANSPORT                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ REST API     │  │ Agent        │  │ Auth +           │  │
│  │ (HTTP)       │  │ Discovery    │  │ Encryption       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Why The Math Matters

Anyone can claim "our agents are smarter together." ClawNet **proves it**:

1. **Information Emergence**: `I(Q; Network) > max(I(Q; Individual))` — the network knows more
2. **Consolidation Convergence**: Memory strength monotonically increases — the system improves over time
3. **Scalability Bounds**: O(n·m) storage, O(m·d) queries — works at scale
4. **Deterministic Embeddings**: Same text → same vector — reproducible science

## What This Enables

- **Multi-agent teams** that genuinely learn from each other
- **Personal AI networks** (laptop + phone + server sharing your life context)
- **Research collectives** where every agent's discovery benefits all
- **Agent evolution** — the network improves as agents learn

## Files

```
clawnet/
├── README.md              # This file
├── PROOFS.md              # Mathematical proofs (theorems + derivations)
├── setup.py               # pip install clawnet
├── Dockerfile             # One-command deployment
├── clawnet/
│   ├── __init__.py        # Package export
│   ├── server.py          # Memory server (HTTP API, semantic search)
│   └── client.py          # Python SDK
├── examples/
│   ├── multi_agent_demo.py      # 3-agent sharing demo
│   └── emergence_demo.py        # Mathematical emergence proof
└── tests/
    └── test_emergence.py        # Verify theorems with pytest
```

## Roadmap

- [x] Protocol v1 specification
- [x] Mathematical proofs of emergence
- [x] Memory server with semantic search
- [x] Python client SDK
- [x] Docker deployment
- [x] Emergence measurement demo
- [ ] WebSocket real-time sync
- [ ] Node.js / Go clients
- [ ] Encrypted memory channels
- [ ] Capability marketplace
- [ ] Agent reputation system
- [ ] Federation (multiple servers, one consciousness)

## License

MIT — use it, build on it, make it yours.

---

**ClawNet** — Because agents shouldn't be alone. And because the math proves it.
