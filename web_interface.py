#!/usr/bin/env python3

import os
import json
import subprocess
import sys
import tempfile
import shutil
import logging
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, Response
from functools import wraps
from dotenv import load_dotenv
import re
from user_agents import parse
from standalone_agent import process_user_input
from utils.agent_loader import load_agent_from_file, load_agent_from_dir
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('library_agent.log')
    ]
)
logger = logging.getLogger('library_agent')

# Import agent functionality
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent_loader import get_loader, get_agent, get_library_agent

# Add path to AGENTS directory
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "AGENTS"))

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, 
            static_folder="static",
            template_folder="templates")

# Set a secret key for session management
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))

# Global dictionary to store loaded agents
loaded_agents = {}

# Define allowed file extensions for upload
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'rtf', 'log', 'csv', 'json', 'xml'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load all available agents at startup
def load_all_agents():
    """Load all agents from the AGENTS directory"""
    agents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "AGENTS")
    
    logger.info(f"Loading agents from: {agents_dir}")
    
    if not os.path.exists(agents_dir):
        logger.warning(f"Warning: Agents directory not found at {agents_dir}")
        return {}
    
    agents = {}
    # Get all directories in the AGENTS folder
    agent_dirs = [d for d in os.listdir(agents_dir) if os.path.isdir(os.path.join(agents_dir, d))]
    
    for agent_dir in agent_dirs:
        agent_path = os.path.join(agents_dir, agent_dir)
        try:
            # Load the agent
            logger.info(f"Attempting to load agent from: {agent_path}")
            agent = load_agent_from_dir(agent_path)
            agents[agent_dir] = agent
            logger.info(f"Successfully loaded agent: {agent_dir}")
        except Exception as e:
            logger.error(f"Error loading agent {agent_dir}: {str(e)}")
            logger.debug(traceback.format_exc())
            
    return agents

# Create and initialize library agent 
def get_library_agent_instance():
    """Get an initialized instance of the LibraryAgent"""
    try:
        logger.info("Initializing LibraryAgent instance")
        
        # Import the LibraryAgent module
        from LibraryAgent.agent import DatabaseManager, scan_folder, read_file_content, classify_content_with_groq
        
        # Create a config object for initialization
        agent_config = {
            "config": {
                "name": "Library Agent",
                "version": "2.0.0",
                "settings": {
                    "debug_mode": True,  # Enable debug mode for more logging
                    "target_folder": "/Volumes/1TB Kingston Sata/Sovereign AI/CLAUDE_MEMORY_BANK",
                    "knowledge_root": "/Volumes/1TB Kingston Sata/Sovereign AI",
                    "kingston_root": "/Volumes/1TB Kingston Sata",
                    "sorted_folder": "/Volumes/1TB Kingston Sata/Sovereign AI/SORTED_DOCUMENTS"
                }
            }
        }
        
        # Initialize the LibraryAgent (this is calling the initialize function)
        logger.info("Calling initialize() function for LibraryAgent")
        from LibraryAgent.agent import initialize
        initialize(agent_config)
        
        # Create DB manager instance
        db_manager = DatabaseManager()
        
        # Verify database connection
        try:
            doc_count = len(db_manager.get_all_documents())
            logger.info(f"Database connection successful. Found {doc_count} documents.")
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            logger.debug(traceback.format_exc())
        
        # Return the relevant functions
        logger.info("LibraryAgent instance initialized successfully")
        return {
            "db_manager": db_manager,
            "scan_folder": scan_folder,
            "read_file_content": read_file_content,
            "classify_content_with_groq": classify_content_with_groq,
            "config": agent_config
        }
    except Exception as e:
        logger.error(f"Error loading LibraryAgent: {str(e)}")
        logger.debug(traceback.format_exc())
        return None

# Routes
@app.route('/')
def index():
    """Render the main page of the application"""
    logger.info("Rendering index page")
    return render_template('index.html', agents=list(loaded_agents.keys()))

@app.route('/browser_error')
def browser_error():
    """Show browser compatibility error page"""
    logger.info("Rendering browser error page")
    return render_template('browser_error.html')

@app.route('/api/agents')
def get_agents():
    """Return a list of available agents"""
    logger.info("API: Fetching list of available agents")
    return jsonify(list(loaded_agents.keys()))

@app.route('/api/process', methods=['POST'])
def process_command():
    """Process a command directed at a specific agent"""
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("API process: No data provided")
            return jsonify({'error': 'No data provided'}), 400
        
        agent_name = data.get('agent')
        command = data.get('command')
        
        logger.info(f"API process: Processing command '{command}' for agent '{agent_name}'")
        
        if not agent_name or not command:
            logger.warning("API process: Missing agent name or command")
            return jsonify({'error': 'Missing agent name or command'}), 400
        
        if agent_name not in loaded_agents:
            logger.error(f"API process: Agent {agent_name} not found")
            return jsonify({'error': f'Agent {agent_name} not found'}), 404
        
        # Process the command with the specified agent
        agent = loaded_agents[agent_name]
        logger.debug(f"Processing command with agent: {agent}")
        response = process_user_input(agent, command)
        logger.info(f"Command processed. Response length: {len(response)}")
        
        return jsonify({'response': response})
    
    except BadRequest:
        logger.error("API process: Invalid JSON data")
        logger.debug(traceback.format_exc())
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        logger.error(f"API process: Unexpected error: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/library')
def library_interface():
    """Interface for library agent operations"""
    logger.info("Rendering library interface page")
    return render_template('library.html')

@app.route('/api/library/scan', methods=['POST'])
def library_scan():
    """API endpoint to scan directories with the library agent"""
    try:
        logger.info("API library/scan: Processing request")
        data = request.json
        logger.debug(f"Request data: {data}")
        
        directory = data.get('directory')
        recursive = data.get('recursive', False)
        
        logger.info(f"Scanning directory: {directory}, recursive: {recursive}")
        
        if not directory:
            logger.warning("API library/scan: No directory path provided")
            return jsonify({"status": "error", "message": "Directory path required"}), 400
            
        if not os.path.exists(directory):
            logger.error(f"API library/scan: Directory not found: {directory}")
            return jsonify({"status": "error", "message": f"Directory not found: {directory}"}), 404
        
        # Get library agent instance
        logger.info("Getting LibraryAgent instance")
        library_agent = get_library_agent_instance()
        if not library_agent:
            logger.error("API library/scan: Failed to initialize library agent")
            return jsonify({"status": "error", "message": "Failed to initialize library agent"}), 500
        
        # Scan the directory
        logger.info(f"Starting folder scan of {directory}")
        file_count = library_agent["scan_folder"](directory, recursive)
        logger.info(f"Scan completed. Processed {file_count} files.")
        
        # Get the scanned documents
        logger.info("Retrieving documents from database")
        db_manager = library_agent["db_manager"]
        documents = db_manager.get_all_documents()
        logger.info(f"Retrieved {len(documents)} documents from database")
        
        # Convert to list for JSON serialization
        doc_list = [documents[filename] for filename in documents]
        
        logger.info("API library/scan: Scan completed successfully")
        return jsonify({
            "status": "success", 
            "result": {
                "count": file_count,
                "documents": doc_list
            }
        })
    except Exception as e:
        logger.error(f"API library/scan: Error scanning directory: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/library/search', methods=['POST'])
def library_search():
    """API endpoint to search documents with library agent"""
    try:
        logger.info("API library/search: Processing request")
        data = request.json
        logger.debug(f"Request data: {data}")
        
        query = data.get('query')
        limit = data.get('limit', 10)
        
        logger.info(f"Searching for: '{query}', limit: {limit}")
        
        if not query:
            logger.warning("API library/search: No search query provided")
            return jsonify({"status": "error", "message": "Search query required"}), 400
        
        # Get library agent instance
        logger.info("Getting LibraryAgent instance")
        library_agent = get_library_agent_instance()
        if not library_agent:
            logger.error("API library/search: Failed to initialize library agent")
            return jsonify({"status": "error", "message": "Failed to initialize library agent"}), 500
        
        # Search documents
        logger.info(f"Searching documents with term: {query}")
        db_manager = library_agent["db_manager"]
        results = db_manager.search_documents(term=query, limit=limit)
        logger.info(f"Found {len(results)} matching documents")
        
        logger.info("API library/search: Search completed successfully")
        return jsonify({"status": "success", "result": results})
    except Exception as e:
        logger.error(f"API library/search: Error searching documents: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/library/stats', methods=['GET'])
def library_stats():
    """API endpoint to get statistics from library agent"""
    try:
        logger.info("API library/stats: Processing request")
        
        # Get library agent instance
        logger.info("Getting LibraryAgent instance")
        library_agent = get_library_agent_instance()
        if not library_agent:
            logger.error("API library/stats: Failed to initialize library agent")
            return jsonify({"status": "error", "message": "Failed to initialize library agent"}), 500
        
        # Get statistics
        logger.info("Retrieving database statistics")
        db_manager = library_agent["db_manager"]
        stats = db_manager.get_stats()
        logger.info(f"Retrieved stats: {stats}")
        
        logger.info("API library/stats: Stats retrieved successfully")
        return jsonify({"status": "success", "result": stats})
    except Exception as e:
        logger.error(f"API library/stats: Error retrieving statistics: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/library/upload', methods=['POST'])
def library_upload():
    """API endpoint to upload files to the library"""
    try:
        logger.info("API library/upload: Processing file upload request")
        
        if 'files' not in request.files:
            logger.warning("API library/upload: No files provided in request")
            return jsonify({"status": "error", "message": "No files provided"}), 400
            
        files = request.files.getlist('files')
        logger.info(f"Received {len(files)} files")
        
        if not files or len(files) == 0:
            logger.warning("API library/upload: Empty files list")
            return jsonify({"status": "error", "message": "No files selected"}), 400
        
        # Get library agent instance
        logger.info("Getting LibraryAgent instance")
        library_agent = get_library_agent_instance()
        if not library_agent:
            logger.error("API library/upload: Failed to initialize library agent")
            return jsonify({"status": "error", "message": "Failed to initialize library agent"}), 500
        
        # Create temporary directory for uploaded files
        upload_dir = os.path.join(tempfile.gettempdir(), 'library_uploads')
        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f"Created temporary directory for uploads: {upload_dir}")
        
        uploaded_files = []
        processed_documents = []
        
        # Save files to temporary directory and process
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                logger.info(f"Saving uploaded file: {filename} to {file_path}")
                file.save(file_path)
                uploaded_files.append(file_path)
            else:
                logger.warning(f"Skipping file {file.filename} - not allowed type")
        
        # Process uploaded files
        for file_path in uploaded_files:
            try:
                logger.info(f"Processing file: {file_path}")
                content = library_agent["read_file_content"](file_path)
                
                if content:
                    filename = os.path.basename(file_path)
                    logger.info(f"Classifying content of {filename}")
                    classification = library_agent["classify_content_with_groq"](content, filename)
                    logger.info(f"Classification result length: {len(classification)}")
                    
                    # Determine target path (where to store the file)
                    target_folder = library_agent["config"]["config"]["settings"]["target_folder"]
                    target_path = os.path.join(target_folder, filename)
                    logger.info(f"Target path for file: {target_path}")
                    
                    # Move file to target location
                    logger.info(f"Creating directory if needed: {os.path.dirname(target_path)}")
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    logger.info(f"Copying file from {file_path} to {target_path}")
                    shutil.copy(file_path, target_path)
                    
                    # Add to database
                    logger.info(f"Adding document to database: {filename}")
                    doc_data = {
                        "file_path": target_path,
                        "classification": classification,
                        "organization": "Uploads",
                        "direction": "Inbox",
                        "file_type": os.path.splitext(filename)[1][1:].upper(),
                        "last_updated": datetime.now().isoformat(),
                        "is_kingston": target_path.startswith(library_agent["config"]["config"]["settings"]["kingston_root"]),
                        "original_path": file_path
                    }
                    
                    db_manager = library_agent["db_manager"]
                    db_manager.add_document(filename, doc_data)
                    processed_documents.append(doc_data)
                    logger.info(f"Document {filename} processed and added to database")
                else:
                    logger.warning(f"Could not read content from file: {file_path}")
            except Exception as e:
                logger.error(f"Error processing uploaded file {file_path}: {str(e)}")
                logger.debug(traceback.format_exc())
        
        # Clean up temporary files
        for file_path in uploaded_files:
            try:
                logger.info(f"Removing temporary file: {file_path}")
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not remove temp file {file_path}: {str(e)}")
        
        logger.info(f"Upload completed. Processed {len(processed_documents)} documents")
        return jsonify({
            "status": "success",
            "result": {
                "count": len(processed_documents),
                "documents": processed_documents
            }
        })
    except Exception as e:
        logger.error(f"API library/upload: Unexpected error: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/library/open', methods=['POST'])
def library_open():
    """API endpoint to open a document"""
    try:
        logger.info("API library/open: Processing request")
        data = request.json
        logger.debug(f"Request data: {data}")
        
        filename = data.get('filename')
        logger.info(f"Opening document: {filename}")
        
        if not filename:
            logger.warning("API library/open: No filename provided")
            return jsonify({"status": "error", "message": "Filename is required"}), 400
        
        # Get library agent instance
        logger.info("Getting LibraryAgent instance")
        library_agent = get_library_agent_instance()
        if not library_agent:
            logger.error("API library/open: Failed to initialize library agent")
            return jsonify({"status": "error", "message": "Failed to initialize library agent"}), 500
        
        # Find document in database
        logger.info(f"Looking up document in database: {filename}")
        db_manager = library_agent["db_manager"]
        all_docs = db_manager.get_all_documents()
        logger.info(f"Retrieved {len(all_docs)} documents from database")
        
        doc = None
        if filename in all_docs:
            logger.info(f"Found exact match for {filename}")
            doc = all_docs[filename]
        else:
            # Try partial match
            logger.info(f"No exact match found, trying partial matching for {filename}")
            for name, doc_data in all_docs.items():
                if filename.lower() in name.lower():
                    logger.info(f"Found partial match: {name}")
                    doc = doc_data
                    break
        
        if not doc:
            logger.error(f"API library/open: Document not found: {filename}")
            return jsonify({"status": "error", "message": f"Document not found: {filename}"}), 404
        
        # Check if file exists
        logger.info(f"Checking if file exists at path: {doc['file_path']}")
        if not os.path.exists(doc['file_path']):
            logger.error(f"API library/open: File no longer exists at {doc['file_path']}")
            return jsonify({"status": "error", "message": f"File no longer exists at {doc['file_path']}"}), 404
        
        # Open file with default application
        try:
            if os.name == 'nt':  # Windows
                logger.info(f"Opening file with Windows startfile: {doc['file_path']}")
                os.startfile(doc['file_path'])
            elif os.name == 'posix':  # macOS/Linux
                logger.info(f"Opening file with subprocess.call('open'): {doc['file_path']}")
                import subprocess
                subprocess.call(('open', doc['file_path']))
            
            logger.info(f"API library/open: Successfully opened {doc['filename']}")
            return jsonify({
                "status": "success",
                "message": f"Opening {doc['filename']}...",
                "path": doc['file_path']
            })
        except Exception as e:
            logger.error(f"API library/open: Error opening file: {str(e)}")
            logger.debug(traceback.format_exc())
            return jsonify({"status": "error", "message": f"Error opening file: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"API library/open: Unexpected error: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/mem0')
def mem0_interface():
    """Interface for mem0 agent operations"""
    logger.info("Rendering mem0 interface page")
    return render_template('mem0.html')

@app.route('/api/mem0/store', methods=['POST'])
def mem0_store():
    """API endpoint to store memory with mem0 agent"""
    data = request.json
    memory_content = data.get('content')
    memory_type = data.get('type', 'note')
    tags = data.get('tags', [])
    
    try:
        logger.info(f"API mem0/store: Storing memory of type {memory_type}")
        result = run_mem0_agent(
            action="store",
            content=memory_content,
            memory_type=memory_type,
            tags=tags,
            output_file=None
        )
        logger.info("API mem0/store: Memory stored successfully")
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        logger.error(f"API mem0/store: Error storing memory: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/mem0/retrieve', methods=['POST'])
def mem0_retrieve():
    """API endpoint to retrieve memories with mem0 agent"""
    data = request.json
    query = data.get('query')
    limit = data.get('limit', 10)
    
    try:
        logger.info(f"API mem0/retrieve: Retrieving memories for query: {query}")
        result = run_mem0_agent(
            action="retrieve",
            query=query,
            limit=limit,
            output_file=None
        )
        logger.info("API mem0/retrieve: Memories retrieved successfully")
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        logger.error(f"API mem0/retrieve: Error retrieving memories: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/mem0/show', methods=['GET'])
def mem0_show():
    """API endpoint to show memories with mem0 agent"""
    try:
        logger.info("API mem0/show: Showing all memories")
        result = run_mem0_agent(
            action="show",
            output_file=None
        )
        logger.info("API mem0/show: Memories displayed successfully")
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        logger.error(f"API mem0/show: Error displaying memories: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

# Main execution
if __name__ == "__main__":
    # Create directories for templates and static files if they don't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), "templates"), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "static"), exist_ok=True)
    
    logger.info("Starting server initialization")
    
    # Load all agents before starting the server
    loaded_agents = load_all_agents()
    logger.info(f"Loaded {len(loaded_agents)} agents: {', '.join(loaded_agents.keys())}")
    
    # Run the Flask app
    logger.info("Starting Flask server on port 8080")
    app.run(debug=True, host="0.0.0.0", port=8080) 