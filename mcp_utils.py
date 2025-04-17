import os
from dotenv import load_dotenv

# Flag to track if Mem0 is available
MEM0_AVAILABLE = False

def check_mem0_available():
    """
    Check if the Mem0 package is available.
    Returns False since we know it's not installed.
    """
    try:
        import importlib.util
        spec = importlib.util.find_spec('mem0')
        return spec is not None
    except:
        return False

def get_mem0_client():
    """
    Get a Mem0 client instance.
    Currently returns None as the mem0 package is not installed.
    """
    print("Warning: Mem0 client not available - package not installed")
    return None

def get_agent_config():
    """Get a configuration dictionary with all settings needed for agents"""
    load_dotenv()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "library.db")
    knowledge_root = os.getenv("KNOWLEDGE_ROOT", "/Volumes/1TB Kingston Sata/Sovereign AI")
    target_folder = os.getenv("TARGET_FOLDER", os.path.join(knowledge_root, "CLAUDE_MEMORY_BANK"))
    return {
        "script_dir": script_dir,
        "db_path": os.getenv("DB_PATH", db_path),
        "knowledge_root": knowledge_root,
        "target_folder": target_folder,
        "kingston_root": os.getenv("KINGSTON_ROOT", "/Volumes/1TB Kingston Sata"),
        "sorted_folder_base": os.getenv("SORTED_FOLDER_BASE", os.path.join(knowledge_root, "SORTED_DOCUMENTS")),
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "llm_provider": os.getenv("LLM_PROVIDER", "openai"),
        "llm_api_key": os.getenv("LLM_API_KEY"),
        "llm_base_url": os.getenv("LLM_BASE_URL"),
        "llm_model": os.getenv("LLM_CHOICE", "gpt-4o-mini"),
        "embedding_model": os.getenv("EMBEDDING_MODEL_CHOICE", "text-embedding-3-small"),
        "mem0_available": check_mem0_available()
    }

def get_groq_headers():
    """Get headers for Groq API requests"""
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")
    return {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }