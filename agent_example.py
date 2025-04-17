#!/usr/bin/env python3

import os
import sys
import argparse
from agent_loader import get_agent, get_library_agent, get_loader

def main():
    parser = argparse.ArgumentParser(description="Agent Loader Example")
    parser.add_argument("--agent", type=str, default="library", help="Agent to load (default: library)")
    parser.add_argument("--search", type=str, help="Search term for library agent")
    parser.add_argument("--list", action="store_true", help="List all available agents")
    parser.add_argument("--config", action="store_true", help="Show agent configuration")
    
    args = parser.parse_args()
    
    # Show configuration
    if args.config:
        loader = get_loader()
        print("Agent Configuration:")
        for key, value in loader.config.items():
            print(f"  {key}: {value}")
        return
    
    # List available agents
    if args.list:
        loader = get_loader()
        all_agents = loader.get_all_agents()
        print(f"Available agents: {list(all_agents.keys())}")
        return
    
    # Load specified agent
    agent_name = args.agent
    try:
        agent = get_agent(agent_name)
        print(f"Successfully loaded agent: {agent_name}")
        
        # Library agent-specific operations
        if agent_name == "library" and args.search:
            if hasattr(agent, "search_documents"):
                results = agent.search_documents(args.search)
                print(f"\nSearch results for '{args.search}':")
                for filename, data in results.items():
                    print(f"\n📄 {filename}")
                    print(f"🔎 {data.get('classification', 'No classification')}")
                    print(f"📂 {data.get('file_path', 'No path')}")
            else:
                import sqlite3
                # Fallback to direct database query
                db_conn = get_loader().get_db_connection()
                cursor = db_conn.cursor()
                cursor.execute(
                    "SELECT filename, classification, file_path FROM documents WHERE filename LIKE ? OR classification LIKE ?",
                    (f'%{args.search}%', f'%{args.search}%')
                )
                print(f"\nSearch results for '{args.search}':")
                for row in cursor.fetchall():
                    print(f"\n📄 {row[0]}")
                    print(f"🔎 {row[1]}")
                    print(f"📂 {row[2]}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 