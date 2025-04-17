#!/usr/bin/env python3

import os
import importlib
import sqlite3
from dotenv import load_dotenv
from typing import Dict, Any, Optional, Union, List
import json
import importlib.util
import sys

# Import utility functions
from mcp_utils import get_mem0_client, check_mem0_available

# Load environment variables
load_dotenv()

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "library.db")

class AgentLoader:
    """
    Simple agent loader for demo purposes
    """
    
    def __init__(self):
        self.agents = {}
        self.config = {}
        self.load_config()
        
    def load_config(self):
        """Load agent configuration from environment variables"""
        self.config = {
            "knowledge_root": os.getenv("KNOWLEDGE_ROOT", "/Volumes/1TB Kingston Sata/Sovereign AI"),
            "target_folder": os.getenv("TARGET_FOLDER", "/Volumes/1TB Kingston Sata/Sovereign AI/CLAUDE_MEMORY_BANK"),
            "available_agents": os.getenv("AVAILABLE_AGENTS", "library").split(","),
        }
    
    def get_agent(self, agent_name: str) -> Any:
        """
        Dummy get_agent method - not actually used in this demo
        """
        return None
    
    def get_all_agents(self) -> Dict[str, Any]:
        """
        Get all available agents - not actually used in this demo
        """
        return self.agents

# Singleton instance for easy access
_loader = None

def get_loader() -> AgentLoader:
    """
    Get the singleton AgentLoader instance
    """
    global _loader
    if _loader is None:
        _loader = AgentLoader()
    return _loader

# Convenience functions
def get_agent(agent_name: str) -> Any:
    """
    Get an agent by name - dummy function for this demo
    """
    return None

def get_library_agent():
    """
    Get the library agent - dummy function for this demo
    """
    return None

def load_agent_from_dir(agent_dir: str) -> Dict[str, Any]:
    """
    Load an agent from a directory containing agent files.
    
    Args:
        agent_dir: Path to the directory containing agent files
        
    Returns:
        Dictionary containing agent data and functions
    """
    if not os.path.isdir(agent_dir):
        raise ValueError(f"Agent directory does not exist: {agent_dir}")
    
    # Check for config.json
    config_path = os.path.join(agent_dir, "config.json")
    if not os.path.exists(config_path):
        raise ValueError(f"Missing config.json in agent directory: {agent_dir}")
    
    # Load config
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in config file: {config_path}")
    
    # Check for required config fields
    required_fields = ["name", "description", "version"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field '{field}' in config: {config_path}")
    
    # Check for agent.py
    agent_py_path = os.path.join(agent_dir, "agent.py")
    if not os.path.exists(agent_py_path):
        raise ValueError(f"Missing agent.py in agent directory: {agent_dir}")
    
    # Load agent.py module
    try:
        spec = importlib.util.spec_from_file_location("agent_module", agent_py_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Could not load agent module: {agent_py_path}")
        
        agent_module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = agent_module
        spec.loader.exec_module(agent_module)
        
        # Check if required functions are defined
        if not hasattr(agent_module, "process_command"):
            raise ValueError(f"Missing required function 'process_command' in agent module: {agent_py_path}")
        
        # Create agent object
        agent = {
            "config": config,
            "dir": agent_dir,
            "process_command": agent_module.process_command
        }
        
        # Add optional functions if they exist
        optional_functions = ["initialize", "cleanup", "get_status"]
        for func_name in optional_functions:
            if hasattr(agent_module, func_name):
                agent[func_name] = getattr(agent_module, func_name)
        
        # Initialize agent if function exists
        if "initialize" in agent:
            agent["initialize"](agent)
        
        return agent
    
    except Exception as e:
        raise ValueError(f"Error loading agent module: {str(e)}")


def load_agent_from_file(agent_file: str) -> Dict[str, Any]:
    """
    Load an agent from a single Python file.
    
    Args:
        agent_file: Path to the agent Python file
        
    Returns:
        Dictionary containing agent data and functions
    """
    if not os.path.isfile(agent_file):
        raise ValueError(f"Agent file does not exist: {agent_file}")
    
    # Load agent module
    try:
        agent_dir = os.path.dirname(agent_file)
        filename = os.path.basename(agent_file)
        module_name = os.path.splitext(filename)[0]
        
        spec = importlib.util.spec_from_file_location(module_name, agent_file)
        if spec is None or spec.loader is None:
            raise ValueError(f"Could not load agent module: {agent_file}")
        
        agent_module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = agent_module
        spec.loader.exec_module(agent_module)
        
        # Check if required attributes and functions are defined
        required_attributes = ["AGENT_NAME", "AGENT_DESCRIPTION", "AGENT_VERSION"]
        for attr in required_attributes:
            if not hasattr(agent_module, attr):
                raise ValueError(f"Missing required attribute '{attr}' in agent module: {agent_file}")
        
        if not hasattr(agent_module, "process_command"):
            raise ValueError(f"Missing required function 'process_command' in agent module: {agent_file}")
        
        # Create agent object
        agent = {
            "config": {
                "name": agent_module.AGENT_NAME,
                "description": agent_module.AGENT_DESCRIPTION,
                "version": agent_module.AGENT_VERSION
            },
            "dir": agent_dir,
            "process_command": agent_module.process_command
        }
        
        # Add optional functions if they exist
        optional_functions = ["initialize", "cleanup", "get_status"]
        for func_name in optional_functions:
            if hasattr(agent_module, func_name):
                agent[func_name] = getattr(agent_module, func_name)
        
        # Initialize agent if function exists
        if "initialize" in agent:
            agent["initialize"](agent)
        
        return agent
    
    except Exception as e:
        raise ValueError(f"Error loading agent module: {str(e)}")

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