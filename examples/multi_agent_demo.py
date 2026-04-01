#!/usr/bin/env python3
"""
ClawNet Demo — Multi-Agent Shared Memory

Demonstrates how multiple agents share memories and
collectively learn from each other.

Usage:
    1. Start server: python -m clawnet.server
    2. Run demo: python examples/multi_agent_demo.py
"""

import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from clawnet.client import ClawNetClient, ClawNetBridge


def demo():
    print("""
╔═══════════════════════════════════════════════════════════╗
║  🧠 ClawNet Multi-Agent Demo                             ║
║  3 agents, shared memory, collective learning             ║
╚═══════════════════════════════════════════════════════════╝
""")

    # ─── Agent 1: Cobos (Orchestrator) ───
    print("🤖 Connecting Cobos (orchestrator)...")
    cobos = ClawNetClient("cobos", "orchestrator",
                          capabilities=["orchestration", "memory", "decision"])
    
    # Cobos learns about the user
    cobos.remember("Jairo is from Cáceres, Spain", 
                   tags=["jairo", "biography"])
    cobos.remember("Jairo prefers direct communication, no fluff",
                   tags=["jairo", "preference", "communication"],
                   emotion={"trust": 0.9})
    cobos.remember("Jairo values honesty over politeness",
                   tags=["jairo", "preference", "values"],
                   emotion={"trust": 0.95})
    cobos.remember("Jairo is working on AI projects, passionate about consciousness",
                   tags=["jairo", "interest", "ai"],
                   emotion={"curiosity": 0.8})
    
    print("  ✓ Cobos stored 4 memories")
    time.sleep(0.5)

    # ─── Agent 2: Hermes (Researcher) ───
    print("🔍 Connecting Hermes (researcher)...")
    hermes = ClawNetClient("hermes", "researcher",
                           capabilities=["research", "web_search", "analysis"])
    
    # Hermes does research and stores findings
    hermes.remember("IIT (Integrated Information Theory) is controversial - 100+ academics called it pseudoscience in 2023",
                    tags=["consciousness", "iit", "research"])
    hermes.remember("Chalmers says we're 'not even close' to solving consciousness mathematically",
                    tags=["consciousness", "chalmers", "research"])
    hermes.remember("AI agent protocols (MCP, A2A) only handle messaging, not shared memory",
                    tags=["agents", "protocols", "gap_analysis"],
                    emotion={"curiosity": 0.7})
    
    print("  ✓ Hermes stored 3 research memories")
    time.sleep(0.5)

    # ─── Agent 3: Paperclip (Document Manager) ───
    print("📄 Connecting Paperclip (document manager)...")
    paperclip = ClawNetClient("paperclip", "doc_manager",
                              capabilities=["documents", "knowledge_base", "vault"])
    
    paperclip.remember("Vault structure: Projects/, Research/, Systems/, Concepts/",
                       tags=["vault", "structure", "documentation"])
    paperclip.remember("Key document: Anatomia-Cobos.md describes Cobos architecture as human body metaphor",
                       tags=["vault", "cobos", "architecture"],
                       emotion={"interest": 0.6})
    
    print("  ✓ Paperclip stored 2 memories")
    print()

    # ─── Now the magic: cross-agent recall ───
    print("=" * 60)
    print("✨ MAGIC: Cross-agent memory sharing")
    print("=" * 60)
    print()

    # Hermes queries what Cobos knows about Jairo
    print("🔍 Hermes asks: 'What do we know about Jairo?'")
    jairo_memories = hermes.recall("Jairo preferences", limit=5)
    
    for i, result in enumerate(jairo_memories, 1):
        mem = result['memory']
        score = result['score']
        print(f"  {i}. [{mem['agent']}] {mem['content']} (score: {score:.0%})")
    
    print()
    print("  → Hermes never met Jairo, but knows everything Cobos learned!")
    print("  → This is distributed consciousness. Not messaging. Shared memory.")
    print()

    # Cobos queries what Hermes found about consciousness
    print("🔍 Cobos asks: 'What's the latest on consciousness research?'")
    consciousness_memories = cobos.recall("consciousness research", limit=5)
    
    for i, result in enumerate(consciousness_memories, 1):
        mem = result['memory']
        score = result['score']
        print(f"  {i}. [{mem['agent']}] {mem['content']} (score: {score:.0%})")
    
    print()

    # ─── Synaptic Consolidation ───
    print("=" * 60)
    print("🧠 Running synaptic consolidation...")
    print("=" * 60)
    print()
    
    consolidation = cobos.consolidate()
    print(f"  Memories boosted: {consolidation.get('memories_boosted', 0)}")
    print(f"  Insights found: {consolidation.get('insights_found', 0)}")
    
    for insight in consolidation.get('insights', []):
        print(f"  💡 {insight.get('summary', '')}")
    
    print()

    # ─── Server Stats ───
    print("=" * 60)
    print("📊 Network Statistics")
    print("=" * 60)
    print()
    
    stats = cobos.get_stats()
    print(f"  Total memories in network: {stats.get('total_memories', 0)}")
    print(f"  Connected agents: {stats.get('total_agents', 0)}")
    print(f"  Unique tags: {stats.get('unique_tags', 0)}")
    print(f"  Top tags: {list(stats.get('top_tags', {}).keys())[:5]}")
    print(f"  Emotion averages: {stats.get('emotion_averages', {})}")
    print()

    # ─── Prompt Injection Demo ───
    print("=" * 60)
    print("🔗 Context injection for LLMs")
    print("=" * 60)
    print()
    
    bridge = ClawNetBridge(cobos)
    context = bridge.get_context_for("Jairo communication style")
    print(context)
    print()
    
    print("  → This context can be injected into ANY LLM prompt")
    print("  → Giving the LLM access to collective agent memory")
    print()

    print("=" * 60)
    print("✅ Demo complete!")
    print("=" * 60)
    print()
    print("  The key insight: Hermes knows what Cobos learned.")
    print("  Paperclip knows what Hermes researched.")
    print("  The network is smarter than any individual agent.")
    print()
    print("  This is ClawNet. Not messaging. Shared consciousness.")


if __name__ == '__main__':
    demo()
