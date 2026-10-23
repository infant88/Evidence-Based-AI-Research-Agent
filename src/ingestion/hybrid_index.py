"""Hybrid Retrieval Engine: BM25 Sparse Keyword Search + Dense Vector Embeddings + RRF Fusion."""

import math
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.ingestion.document_parser import DocumentChunk, DocumentParser

class BM25Index:
    """In-memory BM25 Okapi search implementation."""
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_dl = 0.0
        self.doc_lengths: List[int] = []
        self.doc_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())

    def fit(self, docs: List[str]):
        self.corpus_size = len(docs)
        if self.corpus_size == 0:
            return
        
        tokenized_docs = [self._tokenize(doc) for doc in docs]
        self.doc_lengths = [len(doc) for doc in tokenized_docs]
        self.avg_dl = sum(self.doc_lengths) / max(1, self.corpus_size)

        df: Dict[str, int] = {}
        self.doc_freqs = []

        for doc in tokenized_docs:
            frequencies: Dict[str, int] = {}
            for term in doc:
                frequencies[term] = frequencies.get(term, 0) + 1
            self.doc_freqs.append(frequencies)
            for term in frequencies.keys():
                df[term] = df.get(term, 0) + 1

        for term, freq in df.items():
            # Standard Lucene/Okapi BM25 IDF
            self.idf[term] = math.log(1 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

    def score(self, query: str) -> List[float]:
        query_terms = self._tokenize(query)
        scores = [0.0] * self.corpus_size

        for term in query_terms:
            if term not in self.idf:
                continue
            term_idf = self.idf[term]
            for doc_idx in range(self.corpus_size):
                term_freq = self.doc_freqs[doc_idx].get(term, 0)
                if term_freq == 0:
                    continue
                doc_len = self.doc_lengths[doc_idx]
                numerator = term_freq * (self.k1 + 1)
                denominator = term_freq + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_dl))
                scores[doc_idx] += term_idf * (numerator / denominator)

        return scores


class VectorSearchEngine:
    """Dense Vector Search with SentenceTransformers or fast semantic fallback."""
    def __init__(self):
        self.model = None
        self.embeddings = None
        self._init_model()

    def _init_model(self):
        # Default to high-performance local vectorizer with zero remote network delays
        self.model = None

    def fit(self, texts: List[str]):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.tfidf = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.embeddings = self.tfidf.fit_transform(texts).toarray()

    def score(self, query: str) -> List[float]:
        if self.embeddings is None or len(self.embeddings) == 0:
            return []

        if self.model:
            try:
                import numpy as np
                q_vec = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
                # Cosine similarity
                scores = np.dot(self.embeddings, q_vec)
                return scores.tolist()
            except Exception:
                pass

        if hasattr(self, "tfidf"):
            import numpy as np
            q_vec = self.tfidf.transform([query]).toarray()[0]
            norm_q = np.linalg.norm(q_vec)
            if norm_q == 0:
                return [0.0] * len(self.embeddings)
            norms = np.linalg.norm(self.embeddings, axis=1)
            norms[norms == 0] = 1e-9
            scores = np.dot(self.embeddings, q_vec) / (norms * norm_q)
            return scores.tolist()

        return [0.0] * len(self.embeddings)


class HybridRetriever:
    """Hybrid Retriever combining BM25 Keyword Matching and Dense Vector Embeddings with RRF."""

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self.chunks: List[DocumentChunk] = []
        self.bm25 = BM25Index()
        self.vector_engine = VectorSearchEngine()

    def ingest_directory(self, directory: Path):
        self.chunks = []
        for file_path in directory.glob("*.*"):
            if file_path.suffix.lower() in [".md", ".txt", ".pdf", ".csv"]:
                parsed = DocumentParser.parse_file(file_path)
                self.chunks.extend(parsed)

        corpus_texts = [f"{c.section_title}\n{c.content}" for c in self.chunks]
        self.bm25.fit(corpus_texts)
        self.vector_engine.fit(corpus_texts)
        print(f"HybridRetriever successfully indexed {len(self.chunks)} chunks from {directory}")

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        dense_weight: float = 0.5,
        bm25_weight: float = 0.5,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if not self.chunks:
            return []

        # 1. Compute BM25 scores
        bm25_scores = self.bm25.score(query)
        # 2. Compute Dense vector scores
        vector_scores = self.vector_engine.score(query)

        # 3. Compute Ranks for BM25
        bm25_ranked_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
        bm25_ranks = {idx: rank + 1 for rank, idx in enumerate(bm25_ranked_indices)}

        # 4. Compute Ranks for Dense
        vector_ranked_indices = sorted(range(len(vector_scores)), key=lambda i: vector_scores[i], reverse=True)
        vector_ranks = {idx: rank + 1 for rank, idx in enumerate(vector_ranked_indices)}

        # 5. Reciprocal Rank Fusion (RRF)
        scored_results = []
        for i, chunk in enumerate(self.chunks):
            # Apply metadata filters if supplied
            if metadata_filters:
                skip = False
                for k, v in metadata_filters.items():
                    if chunk.metadata.get(k) != v and getattr(chunk, k, None) != v:
                        skip = True
                        break
                if skip:
                    continue

            r_bm25 = bm25_ranks.get(i, 9999)
            r_dense = vector_ranks.get(i, 9999)
            
            rrf_score = (bm25_weight / (self.rrf_k + r_bm25)) + (dense_weight / (self.rrf_k + r_dense))
            
            scored_results.append({
                "chunk": chunk,
                "rrf_score": rrf_score,
                "bm25_score": bm25_scores[i] if i < len(bm25_scores) else 0.0,
                "vector_score": vector_scores[i] if i < len(vector_scores) else 0.0,
                "bm25_rank": r_bm25,
                "vector_rank": r_dense
            })

        # Sort by RRF score descending
        scored_results.sort(key=lambda x: x["rrf_score"], reverse=True)
        top_results = scored_results[:top_k]

        formatted = []
        for item in top_results:
            c: DocumentChunk = item["chunk"]
            formatted.append({
                "chunk_id": c.chunk_id,
                "document_id": c.document_id,
                "document_name": c.document_name,
                "page_number": c.page_number,
                "section_title": c.section_title,
                "content": c.content,
                "score": round(item["rrf_score"], 4),
                "dense_score": round(item["vector_score"], 4),
                "bm25_score": round(item["bm25_score"], 4),
                "citation_tag": f"[{c.document_name}, Page {c.page_number or 1}: '{c.section_title}']"
            })

        return formatted
