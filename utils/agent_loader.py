"""
Simplified agent loader for utils package
"""

import os
import sys
import importlib.util
from typing import Dict, Any, Optional

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
        
        return agent
    
    except Exception as e:
        raise ValueError(f"Error loading agent module: {str(e)}")

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
    import json
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