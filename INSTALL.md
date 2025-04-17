# Installation and Usage Guide

This guide provides instructions for installing and running the Sovereign AI Agent system.

## Option 1: Local Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sovereign-ai-agents.git
   cd sovereign-ai-agents
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file with your API keys and configuration.

5. Run the example agent:
   ```bash
   python agent_example.py --config
   ```

## Option 2: Docker Installation

### Prerequisites
- Docker
- Docker Compose

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sovereign-ai-agents.git
   cd sovereign-ai-agents
   ```

2. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your API keys and configuration.

4. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

5. Check the logs:
   ```bash
   docker-compose logs -f agent-service
   ```

## Usage

### Command Line Interface

The `agent_example.py` script provides a command-line interface for interacting with the agents:

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

### Python API

You can also use the agents in your Python code:

```python
from agent_loader import get_agent, get_library_agent, get_loader

# Get the library agent
library_agent = get_library_agent()

# Search for documents
results = library_agent.search_documents("your search term")

# Get another agent
custom_agent = get_agent("agent_name")
```

## Troubleshooting

### Mem0 Integration

If you're having issues with the Mem0 integration:

1. Make sure the PostgreSQL database is running
2. Verify your DATABASE_URL in the .env file
3. Check that the mem0 package is installed correctly

### Library Database

If the library agent cannot find or access the database:

1. Check that the DB_PATH environment variable is set correctly
2. Ensure the database file exists and is accessible
3. Verify that the SQLite database has the correct schema 