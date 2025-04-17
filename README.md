# Sovereign AI Agent System

This directory contains various AI agents used by the Sovereign AI system.

## Library Agent

The Library Agent organizes and classifies documents in the system. It provides document scanning, classification, and search capabilities.

### Library Agent Versions

- `library_agent_v2.py` - Latest GUI version with drag-and-drop support
- `library_agent_cli.py` - Command line interface version
- `agent_library.py` - Core library functionality

## Agent Loader System

The `agent_loader.py` provides a unified system for loading and managing different agents. It simplifies the integration of multiple agent types and handles configuration consistently.

### Using the Agent Loader

```python
# Import the agent loader functions
from agent_loader import get_agent, get_library_agent, get_loader

# Get the library agent
library_agent = get_library_agent()

# Get any agent by name
custom_agent = get_agent("agent_name")

# Get the loader object for more control
loader = get_loader()
```

### Example Usage

The `agent_example.py` script demonstrates how to use the agent loader:

```bash
# Show configuration
python agent_example.py --config

# List available agents
python agent_example.py --list

# Use the library agent to search
python agent_example.py --search "your search term"

# Load a different agent
python agent_example.py --agent agent_name
```

## Configuration

Agents are configured using environment variables loaded from the `.env` file. Common settings include:

- `KNOWLEDGE_ROOT` - Base path for knowledge storage
- `TARGET_FOLDER` - Target folder for document scanning
- `GROQ_API_KEY` - API key for Groq LLM service
- `LLM_PROVIDER` - Provider for LLM services (e.g., openai, groq)
- `LLM_API_KEY` - API key for LLM services
- `LLM_CHOICE` - Model choice for LLM (e.g., gpt-4o-mini, llama-4)
- `AVAILABLE_AGENTS` - Comma-separated list of available agents

## Utility Functions

The `mcp_utils.py` file contains common utility functions used by multiple agents.

## Database

The system uses SQLite for document storage (`library.db`).

## Requirements

Python packages required are listed in `requirements.txt`.

## Running the Agents

```bash
# Run the GUI library agent
python library_agent_v2.py

# Run the CLI library agent
python library_agent_cli.py

# Run the agent via the loader
python agent_example.py
```

# Agent Web Interface

A web-based interface for interacting with AI agents.

## Features

- Modern, responsive UI built with Bootstrap 5
- Support for multiple agents with dynamic loading
- Real-time interaction with agents through a chat interface
- Browser compatibility check (Chrome required)
- Code block formatting in agent responses

## Directory Structure

```
agent-repo/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── img/
├── templates/
│   ├── index.html
│   └── browser_error.html
├── web_interface.py
├── agent_loader.py
├── standalone_agent.py
└── requirements.txt
```

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the web interface:

```bash
python web_interface.py
```

3. Open your Chrome browser and navigate to:

```
http://localhost:5000
```

## Agent Structure

Agents should follow this structure:

```
AGENTS/
└── AgentName/
    ├── config.json
    └── agent.py
```

Where:
- `config.json` contains agent metadata (name, description, version, etc.)
- `agent.py` implements the required functions, particularly `process_command()`

## Adding a New Agent

1. Create a new directory in the `AGENTS/` folder
2. Add a `config.json` file with agent metadata
3. Create an `agent.py` file with the required functions
4. Restart the web interface

## License

MIT 