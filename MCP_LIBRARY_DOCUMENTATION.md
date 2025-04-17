# Library Agent MCP Documentation

This document describes the Model Context Protocol (MCP) interface for the Library Agent, which allows other agents to interact with the document classification and management system.

## Overview

The Library Agent provides a shared memory interface through a SQLite database (`library.db`). Other agents can interact with this database directly or through the provided API endpoints.

## Database Schema

The Library Agent stores document metadata in a SQLite database with the following schema:

```sql
CREATE TABLE documents (
    filename TEXT PRIMARY KEY,
    file_path TEXT,
    classification TEXT,
    organization TEXT,
    direction TEXT,
    file_type TEXT,
    last_updated TEXT,
    content_hash TEXT,
    is_kingston BOOLEAN,
    original_path TEXT
)
```

### Fields Explanation

- `filename`: The name of the document file (Primary Key)
- `file_path`: Path to the document file in the file system
- `classification`: AI-generated classification/summary of the document content
- `organization`: Organizational category (e.g., Personal, Work, Projects, Research)
- `direction`: Direction category (e.g., Inbox, Outbox, Archive, Drafts)
- `file_type`: Type of the file (e.g., TXT, PDF, MD)
- `last_updated`: ISO timestamp of when the document was last updated
- `content_hash`: Hash of the file content (for future duplicate detection)
- `is_kingston`: Boolean indicating if the file is on the Kingston drive
- `original_path`: Original path if the file was moved

## API Endpoints

The Library Agent exposes the following API endpoints for integration:

### 1. Scan Directory

```
POST /api/library/scan
```

Scans a directory for documents, processes them, and adds to the database.

**Request:**
```json
{
  "directory": "/path/to/directory",
  "recursive": true
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "count": 10,
    "documents": [...]
  }
}
```

### 2. Search Documents

```
POST /api/library/search
```

Searches the document database.

**Request:**
```json
{
  "query": "search term",
  "limit": 10
}
```

**Response:**
```json
{
  "status": "success",
  "result": [...]
}
```

### 3. Get Statistics

```
GET /api/library/stats
```

Returns statistics about the document database.

**Response:**
```json
{
  "status": "success",
  "result": {
    "total": 100,
    "organizations": {"Personal": 20, "Work": 50, ...},
    "file_types": {"PDF": 30, "TXT": 40, ...},
    "directions": {"Inbox": 80, "Archive": 20, ...},
    "locations": {"true": 70, "false": 30}
  }
}
```

### 4. Upload Files

```
POST /api/library/upload
```

Uploads files to be processed and added to the database.

**Request:** Form data with `files` array

**Response:**
```json
{
  "status": "success",
  "result": {
    "count": 3,
    "documents": [...]
  }
}
```

### 5. Open File

```
POST /api/library/open
```

Opens a document with the system's default application.

**Request:**
```json
{
  "filename": "document.pdf"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Opening document.pdf...",
  "path": "/path/to/document.pdf"
}
```

## Direct Database Access

For agents running in the same environment, direct SQLite database access is also possible. The database file is located at:

```
/path/to/AGENTS/library.db
```

Example Python code to access the database:

```python
import sqlite3

def get_documents_by_category(category):
    with sqlite3.connect('/path/to/AGENTS/library.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM documents WHERE organization = ?', (category,))
        columns = [description[0] for description in c.description]
        return [dict(zip(columns, row)) for row in c.fetchall()]
```

## Document Processing Rules

1. Files on the Kingston drive (`/Volumes/1TB Kingston Sata/`) can be moved and sorted.
2. Files from other locations are indexed but not moved (read-only).
3. Document classification is performed using the Groq API with a LLM.
4. Files are sorted into folders based on their organization and direction categories.

## Integration Examples

### Example 1: Using another Agent to Search Documents

```python
import requests

def find_relevant_documents(query):
    response = requests.post('http://localhost:8080/api/library/search', 
                           json={'query': query, 'limit': 5})
    if response.status_code == 200 and response.json()['status'] == 'success':
        return response.json()['result']
    return []
```

### Example 2: Using Direct DB Access to Get Document Content

```python
import sqlite3

def get_document_content(doc_name):
    # First find the document path in the database
    with sqlite3.connect('/path/to/AGENTS/library.db') as conn:
        c = conn.cursor()
        c.execute('SELECT file_path FROM documents WHERE filename LIKE ?', (f'%{doc_name}%',))
        result = c.fetchone()
        if result:
            file_path = result[0]
            # Now read the file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    return None
``` 