"""
ClawNet Adapters — Connect any agent framework to Context Consistency.

Supported:
- LangChain / LangGraph
- CrewAI
- OpenClaw / Hermes
- Custom agents (any framework)

The adapter pattern means ClawNet doesn't compete with your framework.
It makes your framework better.
"""

from ..client import ClawNetClient, ClawNetBridge


class LangChainAdapter:
    """
    LangChain/LangGraph adapter for ClawNet.
    
    Adds context consistency to LangChain agents without modifying the framework.
    
    Usage:
        from langchain.agents import Agent
        from clawnet.adapters import LangChainAdapter
        
        adapter = LangChainAdapter(llm, clawnet_endpoint="localhost:7890")
        
        # Agent automatically publishes to and reads from ClawNet
        result = agent.run("What do we know about user preferences?")
        # Agent had access to ClawNet context automatically
    """
    
    def __init__(self, llm=None, clawnet_endpoint: str = "localhost:7890",
                 agent_name: str = "langchain_agent"):
        self.llm = llm
        self.agent = ClawNetClient(agent_name, "langchain", 
                                   server=clawnet_endpoint)
        self.bridge = ClawNetBridge(self.agent)
    
    def inject_context(self, query: str, max_memories: int = 5) -> str:
        """Get ClawNet context for injection into LangChain prompts."""
        return self.bridge.get_context_for(query, max_memories)
    
    def publish_result(self, result: str, tags: list = None):
        """Publish agent result to ClawNet."""
        return self.agent.remember(result, tags=tags or ["langchain", "result"])


class CrewAIAdapter:
    """
    CrewAI adapter for ClawNet.
    
    Adds shared memory to CrewAI crews.
    
    Usage:
        from crewai import Agent, Crew, Task
        from clawnet.adapters import CrewAIAdapter
        
        adapter = CrewAIAdapter(clawnet_endpoint="localhost:7890")
        
        # Each crew member shares context via ClawNet
        researcher = Agent(role="Researcher", ...)
        writer = Agent(role="Writer", ...)
        
        adapter.connect_crew([researcher, writer])
    """
    
    def __init__(self, clawnet_endpoint: str = "localhost:7890"):
        self.client = ClawNetClient("crew_coordinator", "crewai",
                                   server=clawnet_endpoint)
        self.connected_agents = []
    
    def connect_crew(self, agents: list):
        """Connect a crew of agents to ClawNet."""
        for i, agent in enumerate(agents):
            name = getattr(agent, 'role', f'agent_{i}').lower().replace(' ', '_')
            self.connected_agents.append({
                'agent': agent,
                'clawnet': ClawNetClient(name, "crew_member",
                                        server=self.client.server)
            })
    
    def share_knowledge(self, agent_index: int, knowledge: str, tags: list = None):
        """A crew member shares knowledge with the crew via ClawNet."""
        if 0 <= agent_index < len(self.connected_agents):
            cn = self.connected_agents[agent_index]['clawnet']
            return cn.remember(knowledge, tags=tags or ["crew_knowledge"])
    
    def get_crew_context(self, query: str) -> list:
        """Get knowledge from all crew members."""
        return self.client.recall(query)


class OpenClawAdapter:
    """
    OpenClaw/Hermes adapter for ClawNet.
    
    Connects OpenClaw instances to the shared context network.
    
    Usage:
        from clawnet.adapters import OpenClawAdapter
        
        adapter = OpenClawAdapter(
            agent_name="cobos",
            role="orchestrator",
            clawnet_endpoint="localhost:7890"
        )
        
        # After OpenClaw processes something important
        adapter.auto_capture("User prefers Spanish communication")
        
        # Get context for OpenClaw prompts
        context = adapter.get_context("user preferences")
    """
    
    def __init__(self, agent_name: str = "openclaw_agent",
                 role: str = "agent",
                 clawnet_endpoint: str = "localhost:7890"):
        self.agent = ClawNetClient(agent_name, role,
                                   server=clawnet_endpoint)
        self.bridge = ClawNetBridge(self.agent)
    
    def auto_capture(self, content: str, context: dict = None):
        """Auto-capture with intelligent tagging."""
        return self.bridge.auto_capture(content, context)
    
    def get_context(self, topic: str) -> str:
        """Get formatted context for prompts."""
        return self.bridge.get_context_for(topic)
    
    def remember(self, content: str, tags: list = None, emotion: dict = None):
        """Store a memory in ClawNet."""
        return self.agent.remember(content, tags=tags, emotion=emotion)
    
    def recall(self, query: str, limit: int = 10):
        """Query ClawNet memories."""
        return self.agent.recall(query, limit=limit)
