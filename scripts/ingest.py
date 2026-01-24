"""
Document ingestion script.

Reads documents from the data/documents directory,
chunks them, generates embeddings, and uploads to Qdrant.

Usage:
    python -m scripts.ingest
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple
from uuid import uuid4

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(project_root / ".env")

from backend.core.exceptions import DocumentIngestionError
from backend.core.logging_config import get_logger, setup_logging
from backend.rag.embeddings import get_embeddings_client
from backend.rag.vectorstore import get_vectorstore_client

# Setup logging
setup_logging("INFO")
logger = get_logger(__name__)

# Document directory
DOCUMENTS_DIR = project_root / "backend" / "data" / "documents"

# Supported file extensions
SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown"}

# Chunking settings
CHUNK_SIZE = 500  # characters
CHUNK_OVERLAP = 50  # characters


def read_document(file_path: Path) -> str:
    """
    Read a document file.
    
    Args:
        file_path: Path to the document
        
    Returns:
        Document content as string
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {str(e)}")
        raise DocumentIngestionError(
            message=f"Failed to read document: {file_path.name}",
            details={"error": str(e)},
        )


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text.strip():
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # Try to break at sentence or paragraph boundary
        if end < text_length:
            # Look for paragraph break
            para_break = text.rfind("\n\n", start, end)
            if para_break > start + chunk_size // 2:
                end = para_break + 2
            else:
                # Look for sentence break
                for sep in [". ", "! ", "? ", "\n"]:
                    sent_break = text.rfind(sep, start, end)
                    if sent_break > start + chunk_size // 2:
                        end = sent_break + len(sep)
                        break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start with overlap
        start = end - chunk_overlap if end < text_length else text_length
    
    return chunks


def discover_documents() -> List[Tuple[Path, str]]:
    """
    Discover all documents in the documents directory.
    
    Returns:
        List of (file_path, source_name) tuples
    """
    documents = []
    
    if not DOCUMENTS_DIR.exists():
        logger.warning(f"Documents directory does not exist: {DOCUMENTS_DIR}")
        return documents
    
    for file_path in DOCUMENTS_DIR.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            source_name = file_path.relative_to(DOCUMENTS_DIR).as_posix()
            documents.append((file_path, source_name))
            logger.info(f"Discovered document: {source_name}")
    
    return documents


def ingest_documents() -> int:
    """
    Main ingestion function.
    
    Reads all documents, chunks them, generates embeddings,
    and uploads to Qdrant.
    
    Returns:
        Number of chunks ingested
    """
    logger.info("Starting document ingestion")
    
    # Discover documents
    documents = discover_documents()
    
    if not documents:
        logger.warning("No documents found to ingest")
        print("\n⚠️  No documents found!")
        print(f"   Place your documents in: {DOCUMENTS_DIR}")
        print(f"   Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")
        return 0
    
    logger.info(f"Found {len(documents)} documents to ingest")
    
    # Initialize clients
    embeddings_client = get_embeddings_client()
    vectorstore_client = get_vectorstore_client()
    
    # Get embedding dimension
    embedding_dim = embeddings_client.get_embedding_dimension()
    logger.info(f"Embedding dimension: {embedding_dim}")
    
    # Ensure collection exists
    vectorstore_client.ensure_collection_exists(embedding_dim)
    
    # Process each document
    all_chunks = []
    all_metadata = []
    
    for file_path, source_name in documents:
        logger.info(f"Processing: {source_name}")
        
        # Read document
        content = read_document(file_path)
        
        # Chunk document
        chunks = chunk_text(content)
        logger.info(f"  Created {len(chunks)} chunks")
        
        # Add chunks with metadata
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadata.append({
                "source": source_name,
                "chunk_index": i,
                "total_chunks": len(chunks),
            })
    
    if not all_chunks:
        logger.warning("No chunks created from documents")
        return 0
    
    logger.info(f"Total chunks to embed: {len(all_chunks)}")
    
    # Generate embeddings (in batches to avoid rate limits)
    batch_size = 50
    all_embeddings = []
    
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        logger.info(f"Embedding batch {i // batch_size + 1}/{(len(all_chunks) - 1) // batch_size + 1}")
        
        embeddings = embeddings_client.embed_texts(batch, input_type="document")
        all_embeddings.extend(embeddings)
    
    # Generate IDs
    ids = [str(uuid4()) for _ in range(len(all_chunks))]
    
    # Upload to Qdrant
    logger.info("Uploading to Qdrant...")
    count = vectorstore_client.upsert_documents(
        embeddings=all_embeddings,
        documents=all_chunks,
        metadata_list=all_metadata,
        ids=ids,
    )
    
    logger.info(f"Successfully ingested {count} chunks")
    
    # Print summary
    print("\n✅ Ingestion complete!")
    print(f"   Documents processed: {len(documents)}")
    print(f"   Chunks created: {count}")
    print(f"   Collection: {vectorstore_client.collection_name}")
    
    return count


def main():
    """Main entry point."""
    print("\n📚 Document Ingestion Script")
    print("=" * 40)
    
    try:
        count = ingest_documents()
        if count > 0:
            print("\n🎉 Your documents are now ready for RAG queries!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        print(f"\n❌ Ingestion failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
