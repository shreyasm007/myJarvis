"""
Utility functions for the Streamlit frontend.
"""

import json
from pathlib import Path
from typing import List

from backend.rag.vectorstore import get_vectorstore_client


def load_logs(log_file: str, tail_lines: int = 100, project_root: Path = None) -> List[str]:
    """
    Load the last N lines from a log file.
    
    Args:
        log_file: Name of the log file
        tail_lines: Number of lines to load
        project_root: Project root path
        
    Returns:
        List of log lines
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent
        
    log_path = project_root / "logs" / log_file
    if not log_path.exists():
        return []
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return lines[-tail_lines:]
    except Exception as e:
        return [f"Error reading log: {str(e)}"]


def parse_log_entry(line: str) -> dict:
    """
    Parse a JSON log entry.
    
    Args:
        line: Log line to parse
        
    Returns:
        Dictionary with parsed log entry
    """
    try:
        return json.loads(line)
    except:
        return {"message": line.strip(), "levelname": "INFO"}


def get_db_stats() -> dict:
    """
    Get database statistics from Qdrant.
    
    Returns:
        Dictionary with collection statistics
    """
    try:
        vectorstore = get_vectorstore_client()
        info = vectorstore.get_collection_info()
        return info
    except Exception as e:
        return {"error": str(e)}


def format_context_display(contexts: list) -> str:
    """
    Format retrieved contexts for display.
    
    Args:
        contexts: List of context dictionaries
        
    Returns:
        Formatted HTML string
    """
    if not contexts:
        return ""
    
    html_parts = []
    for i, ctx in enumerate(contexts):
        score = ctx.get('score', 0)
        source = ctx.get('metadata', {}).get('source', 'Unknown')
        content = ctx.get('content', '')[:500]
        
        html_parts.append(f"""
        <div class="retrieved-context">
            <strong>Document {i+1}</strong> (Score: {score:.3f})<br/>
            <strong>Source:</strong> {source}<br/>
            <strong>Content:</strong> {content}...
        </div>
        """)
    
    return "\n".join(html_parts)
