#!/usr/bin/env python3

import os
import importlib
import sqlite3
from dotenv import load_dotenv
from typing import Dict, Any, Optional, Union, List

# Import utility functions
from mcp_utils import get_mem0_client, check_mem0_available

# Load environment variables
load_dotenv()

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "library.db")

class AgentLoader:
    """
    AgentLoader provides a unified interface to load and access various agents
    in the system. It dynamically loads agent modules based on configuration.
    """
    
    def __init__(self):
        self.agents = {}
        self.config = {}
        self.load_config()
        
    def load_config(self):
        """Load agent configuration from environment variables"""
        # Check if mem0 is available
        mem0_available = check_mem0_available()
        
        self.config = {
            "knowledge_root": os.getenv("KNOWLEDGE_ROOT", "/Volumes/1TB Kingston Sata/Sovereign AI"),
            "target_folder": os.getenv("TARGET_FOLDER", "/Volumes/1TB Kingston Sata/Sovereign AI/CLAUDE_MEMORY_BANK"),
            "db_path": os.getenv("DB_PATH", DB_PATH),
            "llm_provider": os.getenv("LLM_PROVIDER", "openai"),
            "llm_api_key": os.getenv("LLM_API_KEY"),
            "llm_base_url": os.getenv("LLM_BASE_URL"),
            "llm_model": os.getenv("LLM_CHOICE", "gpt-4o-mini"),
            "embedding_model": os.getenv("EMBEDDING_MODEL_CHOICE", "text-embedding-3-small"),
            "groq_api_key": os.getenv("GROQ_API_KEY"),
            "available_agents": os.getenv("AVAILABLE_AGENTS", "library").split(","),
            "mem0_available": mem0_available
        }
    
    def get_agent(self, agent_name: str) -> Any:
        """
        Get an instance of the specified agent.
        If the agent is already loaded, returns the existing instance.
        Otherwise, attempts to load and initialize the agent.
        
        Args:
            agent_name (str): Name of the agent to load
            
        Returns:
            Any: The agent instance if found, None otherwise
        """
        if agent_name in self.agents:
            return self.agents[agent_name]
        
        if agent_name not in self.config["available_agents"]:
            raise ValueError(f"Agent '{agent_name}' is not configured as an available agent")
        
        try:
            if agent_name == "library":
                return self._load_library_agent()
            else:
                # Dynamic loading for future agent types
                module_name = f"{agent_name}_agent"
                try:
                    module = importlib.import_module(module_name)
                    agent_class = getattr(module, f"{agent_name.title()}Agent")
                    self.agents[agent_name] = agent_class(self.config)
                    return self.agents[agent_name]
                except (ImportError, AttributeError) as e:
                    print(f"Error loading agent '{agent_name}': {str(e)}")
                    return None
        except Exception as e:
            print(f"Error initializing agent '{agent_name}': {str(e)}")
            return None
    
    def _load_library_agent(self) -> Any:
        """
        Load the library agent based on available implementations
        """
        try:
            # Try to import the library agent module
            from library_agent_v2 import DatabaseManager
            
            # Initialize the database manager
            db_manager = DatabaseManager()
            self.agents["library"] = db_manager
            return db_manager
        except ImportError:
            try:
                # Fallback to the basic agent library
                import agent_library
                self.agents["library"] = agent_library
                return agent_library
            except ImportError:
                print("Could not load any library agent implementation")
                return None
    
    def get_all_agents(self) -> Dict[str, Any]:
        """
        Get all available agents
        
        Returns:
            Dict[str, Any]: Dictionary of agent name -> agent instance
        """
        # Lazy load all configured agents
        for agent_name in self.config["available_agents"]:
            if agent_name not in self.agents:
                self.get_agent(agent_name)
        
        return self.agents
    
    def get_db_connection(self) -> sqlite3.Connection:
        """
        Get a connection to the SQLite database
        
        Returns:
            sqlite3.Connection: Database connection
        """
        return sqlite3.connect(self.config["db_path"])
    
    def get_mem0(self):
        """
        Get a Mem0 client for memory operations
        
        Returns:
            Mem0: Initialized Mem0 client or None if not available
        """
        if not self.config["mem0_available"]:
            print("Warning: Mem0 is not available. The 'mem0' package is not installed.")
            return None
            
        try:
            return get_mem0_client()
        except Exception as e:
            print(f"Error initializing Mem0 client: {str(e)}")
            return None

# Singleton instance for easy access
_loader = None

def get_loader() -> AgentLoader:
    """
    Get the singleton AgentLoader instance
    
    Returns:
        AgentLoader: The loader instance
    """
    global _loader
    if _loader is None:
        _loader = AgentLoader()
    return _loader

# Convenience functions
def get_agent(agent_name: str) -> Any:
    """
    Get an agent by name
    
    Args:
        agent_name (str): Name of the agent to get
        
    Returns:
        Any: The agent instance
    """
    return get_loader().get_agent(agent_name)

def get_library_agent():
    """
    Get the library agent
    
    Returns:
        Any: The library agent instance
    """
    return get_loader().get_agent("library")

# Example usage
if __name__ == "__main__":
    # Example: Get the library agent
    library_agent = get_library_agent()
    if library_agent:
        print("Successfully loaded library agent")
    else:
        print("Failed to load library agent")
    
    # Example: Get all available agents
    all_agents = get_loader().get_all_agents()
    print(f"Available agents: {list(all_agents.keys())}") 