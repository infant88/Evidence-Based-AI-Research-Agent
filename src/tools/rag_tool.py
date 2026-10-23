"""RAG Retrieval Tool interfacing with the Hybrid Index."""

from typing import Dict, Any, List, Optional
from config.config import settings, DOCS_DIR
from src.ingestion.hybrid_index import HybridRetriever

class RAGTool:
    """Standardized tool interface for Hybrid Document Retrieval."""

    def __init__(self, docs_dir=DOCS_DIR):
        self.retriever = HybridRetriever(rrf_k=settings.RRF_K)
        self.retriever.ingest_directory(docs_dir)

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        results = self.retriever.retrieve(query, top_k=top_k, metadata_filters=filters)
        formatted_chunks = []
        for r in results:
            formatted_chunks.append({
                "chunk_id": r["chunk_id"],
                "document_name": r["document_name"],
                "page": r["page_number"],
                "section": r["section_title"],
                "content": r["content"],
                "score": r["score"],
                "citation": r["citation_tag"]
            })

        return {
            "success": True,
            "query": query,
            "count": len(formatted_chunks),
            "chunks": formatted_chunks
        }
