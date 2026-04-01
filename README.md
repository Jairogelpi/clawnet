# 🧠 ClawNet — Agent Memory Portability Protocol

**The protocol that lets AI agents keep their memories when they change frameworks.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)]()
[![LangChain Compatible](https://img.shields.io/badge/LangChain-Compatible-yellow.svg)]()
[![Real Systems Tested](https://img.shields.io/badge/Real%20Systems-14-tested-red.svg)]()

```
  LangChain agent learns something → stores in ClawNet
  CrewAI agent queries ClawNet     → inherits that knowledge
  OpenClaw agent wakes up           → sees everything
  
  Same memory. Different frameworks. Zero transfer effort.
```

## The Problem

Today, your agent's memory is trapped inside its framework:
- Build with LangChain? Memory dies with LangChain.
- Switch to CrewAI? Start from zero.
- Use multiple frameworks? Each one is an island.

**Nobody else is solving this.** MCP connects agents to tools. A2A connects agents to agents. But when an agent changes framework, it loses everything.

## The Solution

ClawNet is a **portable memory layer** that lives outside any framework.

Your agent's experiences, learned facts, and context — stored once, accessible from anywhere.

| What | Before ClawNet | After ClawNet |
|------|----------------|---------------|
| Switch frameworks | Lose everything | Keep all memories |
| Multiple frameworks | Each isolated | Shared memory |
| Agent restarts | Start from zero | Resume with context |
| Debugging | "Why did this happen?" | Full lineage trace |
| Agent collisions | Data corruption | Context locking |

## Quick Start

```bash
pip install clawnet
```

```python
from clawnet import ClawNetClient

# Works with ANY framework
agent = ClawNetClient("my_agent", "researcher")

# Store something
agent.remember("User prefers Spanish, direct communication")

# Another agent (any framework) inherits this instantly
other_agent = ClawNetClient("other_agent", "writer")
other_agent.recall("user preferences")
# → ["User prefers Spanish, direct communication"]
```

## Features That Don't Exist Anywhere Else

### 1. Agent Memory Portability 🔄
```
Your agent's memory lives in ClawNet, not the framework.
Switch LangChain → CrewAI → OpenClaw. Keep everything.
```

### 2. Context Locking 🔒
```
Prevent agent collisions. Like database row locks, but for AI context.
Two agents can't overwrite each other's work.
```

### 3. Context Lineage 📜
```
Full audit trail of every decision.
"Why did this happen?" → query lineage → answer.
```

### 4. Framework-Agnostic ♾️
```
LangChain ✅  CrewAI ✅  OpenClaw ✅  Custom ✅
One protocol. All frameworks. Shared memory.
```

## Real Systems Tested

ClawNet is tested against **14 real running systems**, not simulations:

```
┌────────────────────────────────────────────────────────────┐
│  Systems on this server that ClawNet connects:             │
│                                                            │
│  🐳 Docker Containers:                                    │
│     • deer-flow-gateway    (multi-agent research)         │
│     • paperclip            (document management)          │
│     • superagent-n8n       (workflow automation)          │
│     • review-ai            (code review)                  │
│     • superagent-obsidian  (knowledge base)               │
│     • + 7 more containers                                 │
│                                                            │
│  🖥️ Processes:                                             │
│     • OpenClaw gateway (this process)                     │
│     • Hermes CLI agent                                    │
│                                                            │
│  Benchmark Results:                                        │
│     • Locking:    ✅ Prevents real collisions              │
│     • Inheritance: ✅ 14 systems share context             │
│     • Lineage:    ✅ Full workflow traceability            │
└────────────────────────────────────────────────────────────┘
```

## Why ClawNet, Not Another Framework

**ClawNet is NOT a framework.** It's the memory layer that makes all frameworks work together.

```
MCP   = Agent → Tools
A2A   = Agent → Agent (messaging)
ClawNet = Agent → Memory → All Agents (portable context)
```

| Protocol | What it does | Memory portability | Context locking | Lineage |
|----------|-------------|-------------------|-----------------|---------|
| MCP | Tool access | ❌ | ❌ | ❌ |
| A2A | Agent messaging | ❌ | ❌ | ❌ |
| CrewAI | Multi-agent workflows | ❌ | ❌ | ❌ |
| **ClawNet** | **Portable agent memory** | **✅** | **✅** | **✅** |

## Install

```bash
pip install clawnet
```

## Run

```bash
# Memory server
clawnet-server --port 7890

# Or with v2 (WebSocket + Context APIs)
clawnet-server-v2 --port 7890
```

## Benchmarks

```bash
# Real systems benchmark (14 actual systems)
python examples/real_systems_benchmark.py

# Context Consistency demo (Locking + Lineage)
python examples/context_consistency_demo.py

# Isolation vs Connection comparison
python examples/benchmark_isolation_vs_connection.py
```

## Documentation

- [AGENT_PORTABILITY.md](AGENT_PORTABILITY.md) — The core insight
- [PROOFS.md](PROOFS.md) — Mathematical proofs of emergence
- [EXPERIMENT.md](EXPERIMENT.md) — Why this cannot be refuted
- [clawnet/protocol.py](clawnet/protocol.py) — Context Locking + Lineage implementation

## The Revolution

Other protocols connect agents to tools or to each other.

**ClawNet gives agents memory that survives everything — including switching frameworks.**

This is the missing infrastructure layer for the agentic era.

## License

MIT
