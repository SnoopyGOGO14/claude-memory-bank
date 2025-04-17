#!/usr/bin/env python3

import os
import sys
import argparse
import json
from datetime import datetime
from agent_loader import get_agent, get_library_agent, get_loader
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("standalone_agent")

def run_library_agent(args):
    """Run the library agent with the given arguments"""
    print(f"Running library agent...")
    
    # Get the library agent
    library_agent = get_library_agent()
    
    if not library_agent:
        print("Error: Could not load library agent")
        return False
    
    if args.scan:
        # Scan the specified directory
        scan_dir = args.scan if os.path.isdir(args.scan) else os.path.dirname(args.scan)
        if not os.path.exists(scan_dir):
            print(f"Error: Directory {scan_dir} does not exist")
            return False
        
        print(f"Scanning directory: {scan_dir}")
        
        # Check which scanning function is available
        if hasattr(library_agent, 'scan_directory'):
            library_agent.scan_directory(scan_dir)
        elif hasattr(library_agent, 'scan_all_files'):
            library_agent.scan_all_files()
        else:
            print("Error: Library agent does not support scanning")
            return False
            
        print("Scan complete")
        
    elif args.search:
        # Search for documents
        print(f"Searching for: {args.search}")
        
        if hasattr(library_agent, 'search_documents'):
            results = library_agent.search_documents(args.search)
            
            if not results:
                print("No results found")
                return True
                
            print(f"\nFound {len(results)} results:")
            
            for filename, data in results.items():
                print(f"\n📄 {filename}")
                print(f"🔎 {data.get('classification', 'No classification')}")
                print(f"📂 {data.get('file_path', 'No path')}")
                
            # Save results to a file if requested
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\nResults saved to {args.output}")
        else:
            print("Error: Library agent does not support searching")
            return False
    
    elif args.stats:
        # Show statistics
        print("Library statistics:")
        
        if hasattr(library_agent, 'get_all_documents'):
            all_docs = library_agent.get_all_documents()
            
            if not all_docs:
                print("No documents in the library")
                return True
                
            # Count by file type
            file_types = {}
            for doc in all_docs.values():
                file_type = doc.get('file_type', 'UNKNOWN')
                file_types[file_type] = file_types.get(file_type, 0) + 1
                
            print(f"Total documents: {len(all_docs)}")
            print("\nBy file type:")
            for file_type, count in sorted(file_types.items()):
                print(f"  {file_type}: {count}")
                
            # Count by organization
            orgs = {}
            for doc in all_docs.values():
                org = doc.get('organization', 'UNKNOWN')
                orgs[org] = orgs.get(org, 0) + 1
                
            print("\nBy organization:")
            for org, count in sorted(orgs.items()):
                print(f"  {org}: {count}")
        else:
            print("Error: Library agent does not support statistics")
            return False
    
    return True

def run_mem0_agent(args):
    """Run the mem0 agent with the given arguments"""
    loader = get_loader()
    
    if not loader.config.get('mem0_available', False):
        print("Error: Mem0 is not available. Please install the mem0 package.")
        return False
    
    # Get the mem0 client
    mem0 = loader.get_mem0()
    
    if not mem0:
        print("Error: Could not initialize Mem0 client")
        return False
    
    if args.store:
        # Store a memory
        content = args.store
        timestamp = datetime.now().isoformat()
        metadata = {"source": "standalone_agent", "timestamp": timestamp}
        
        try:
            mem0.store(content=content, metadata=metadata)
            print(f"Memory stored successfully")
        except Exception as e:
            print(f"Error storing memory: {str(e)}")
            return False
    
    elif args.retrieve:
        # Retrieve memories
        query = args.retrieve
        limit = args.limit or 5
        
        try:
            memories = mem0.retrieve(query=query, limit=limit)
            
            if not memories:
                print("No memories found")
                return True
            
            print(f"\nFound {len(memories)} memories:")
            
            for i, memory in enumerate(memories, 1):
                print(f"\n--- Memory {i} ---")
                print(f"Content: {memory.content}")
                print(f"Metadata: {memory.metadata}")
                
            # Save results to a file if requested
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump([
                        {"content": m.content, "metadata": m.metadata} 
                        for m in memories
                    ], f, indent=2)
                print(f"\nResults saved to {args.output}")
        except Exception as e:
            print(f"Error retrieving memories: {str(e)}")
            return False
    
    else:
        print("Error: No Mem0 operation specified")
        return False
    
    return True

def process_user_input(agent: Dict[str, Any], user_input: str) -> str:
    """
    Process user input using the specified agent.
    
    Args:
        agent: The agent object (loaded from agent_loader)
        user_input: User's command/question
        
    Returns:
        Agent's response as a string
    """
    logger.info(f"Processing user input with agent: {agent['config']['name']}")
    
    try:
        # Call the agent's process_command function
        response = agent["process_command"](agent, user_input)
        
        # If the response is not a string, convert it to a string
        if not isinstance(response, str):
            if isinstance(response, (dict, list)):
                response = json.dumps(response, indent=2)
            else:
                response = str(response)
        
        return response
    
    except Exception as e:
        error_msg = f"Error processing command: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


def create_demo_agent() -> Dict[str, Any]:
    """
    Create a simple demo agent for testing purposes.
    
    Returns:
        Demo agent object
    """
    def process_command(agent: Dict[str, Any], command: str) -> str:
        """Demo agent command processor"""
        if not command:
            return "Please enter a command."
        
        command = command.lower()
        
        if "hello" in command:
            return f"Hello! I'm {agent['config']['name']}, a demo agent."
        
        elif "help" in command:
            return (
                "Demo Agent Help:\n"
                "- hello: Say hello to the agent\n"
                "- help: Show this help message\n"
                "- status: Show agent status\n"
                "- echo [text]: Echo back the text\n"
                "- add [x] [y]: Add two numbers"
            )
        
        elif "status" in command:
            return f"Agent status: Running\nName: {agent['config']['name']}\nVersion: {agent['config']['version']}"
        
        elif command.startswith("echo "):
            text = command[5:].strip()
            return f"Echo: {text}"
        
        elif command.startswith("add "):
            parts = command[4:].strip().split()
            try:
                if len(parts) < 2:
                    return "Please provide two numbers."
                x = float(parts[0])
                y = float(parts[1])
                return f"{x} + {y} = {x + y}"
            except ValueError:
                return "Please provide valid numbers."
        
        else:
            return (
                f"I don't understand '{command}'.\n"
                "Type 'help' to see available commands."
            )
    
    # Create the demo agent
    demo_agent = {
        "config": {
            "name": "Demo Agent",
            "description": "A simple demo agent for testing",
            "version": "1.0.0"
        },
        "dir": os.path.dirname(os.path.abspath(__file__)),
        "process_command": process_command
    }
    
    return demo_agent

def main():
    parser = argparse.ArgumentParser(description="Standalone Agent Runner")
    subparsers = parser.add_subparsers(dest="agent", help="Agent to run")
    
    # Library agent
    library_parser = subparsers.add_parser("library", help="Run the library agent")
    library_group = library_parser.add_mutually_exclusive_group(required=True)
    library_group.add_argument("--scan", type=str, help="Scan directory or file for the library")
    library_group.add_argument("--search", type=str, help="Search for documents in the library")
    library_group.add_argument("--stats", action="store_true", help="Show library statistics")
    library_parser.add_argument("--output", type=str, help="Output file for search results (JSON format)")
    
    # Mem0 agent
    mem0_parser = subparsers.add_parser("mem0", help="Run the Mem0 agent")
    mem0_group = mem0_parser.add_mutually_exclusive_group(required=True)
    mem0_group.add_argument("--store", type=str, help="Store a memory")
    mem0_group.add_argument("--retrieve", type=str, help="Retrieve memories based on query")
    mem0_parser.add_argument("--limit", type=int, help="Limit the number of results")
    mem0_parser.add_argument("--output", type=str, help="Output file for search results (JSON format)")
    
    # Config
    config_parser = subparsers.add_parser("config", help="Show configuration")
    config_parser.add_argument("--verbose", action="store_true", help="Show detailed configuration")
    
    args = parser.parse_args()
    
    if not args.agent:
        parser.print_help()
        return 1
    
    # Show configuration
    if args.agent == "config":
        loader = get_loader()
        print("Agent Configuration:")
        
        if args.verbose:
            for key, value in loader.config.items():
                print(f"  {key}: {value}")
        else:
            # Show simplified configuration
            for key in ["knowledge_root", "target_folder", "available_agents", "llm_provider", "mem0_available"]:
                if key in loader.config:
                    print(f"  {key}: {loader.config[key]}")
        
        return 0
    
    # Run the appropriate agent
    if args.agent == "library":
        success = run_library_agent(args)
    elif args.agent == "mem0":
        success = run_mem0_agent(args)
    else:
        print(f"Error: Unknown agent '{args.agent}'")
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    # Test the demo agent
    demo_agent = create_demo_agent()
    
    print(f"Testing {demo_agent['config']['name']} v{demo_agent['config']['version']}")
    print("Type 'exit' to quit.")
    print()
    
    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            break
        
        response = process_user_input(demo_agent, user_input)
        print(response)
        print()
    
    sys.exit(main()) 