"""Document parsing and hierarchical contextual chunking."""

import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

class DocumentChunk:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        document_name: str,
        document_type: str,
        page_number: Optional[int],
        section_title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.document_name = document_name
        self.document_type = document_type
        self.page_number = page_number
        self.section_title = section_title
        self.content = content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_name": self.document_name,
            "document_type": self.document_type,
            "page_number": self.page_number,
            "section_title": self.section_title,
            "content": self.content,
            "metadata": self.metadata
        }

class DocumentParser:
    """Parses corporate reports, memos, and files into structured chunks."""

    @staticmethod
    def parse_file(file_path: Path) -> List[DocumentChunk]:
        suffix = file_path.suffix.lower()
        if suffix in [".md", ".txt"]:
            return DocumentParser._parse_markdown(file_path)
        elif suffix == ".pdf":
            return DocumentParser._parse_pdf(file_path)
        elif suffix == ".csv":
            return DocumentParser._parse_csv(file_path)
        else:
            return DocumentParser._parse_text(file_path)

    @staticmethod
    def _parse_markdown(file_path: Path) -> List[DocumentChunk]:
        text = file_path.read_text(encoding="utf-8")
        doc_name = file_path.name
        
        # Extract Document ID if present
        doc_id_match = re.search(r"\*\*Document ID:\*\*\s*([A-Za-z0-9\-]+)", text)
        doc_id = doc_id_match.group(1) if doc_id_match else file_path.stem

        # Split into sections based on ## headers
        sections = re.split(r"\n(?=##\s+)", text)
        chunks: List[DocumentChunk] = []

        for idx, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue

            # Inferred title
            lines = section.split("\n")
            header_line = lines[0]
            section_title = header_line.replace("#", "").strip()
            
            # Detect page number if noted in header or text e.g. (Page 2)
            page_match = re.search(r"\(Page\s*(\d+)\)", section, re.IGNORECASE)
            page_num = int(page_match.group(1)) if page_match else (idx + 1)

            chunk_id = f"{doc_id}_c{idx+1}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=doc_id,
                    document_name=doc_name,
                    document_type="markdown",
                    page_number=page_num,
                    section_title=section_title,
                    content=section,
                    metadata={"char_len": len(section), "source_path": str(file_path)}
                )
            )

        return chunks

    @staticmethod
    def _parse_pdf(file_path: Path) -> List[DocumentChunk]:
        # Fallback to text parser if PDF parser fails or parse using pypdf
        chunks = []
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            doc_id = file_path.stem
            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    chunk_id = f"{doc_id}_p{page_idx+1}"
                    chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            document_id=doc_id,
                            document_name=file_path.name,
                            document_type="pdf",
                            page_number=page_idx + 1,
                            section_title=f"Page {page_idx+1}",
                            content=page_text.strip(),
                            metadata={"page_count": len(reader.pages)}
                        )
                    )
        except Exception:
            pass
        return chunks

    @staticmethod
    def _parse_csv(file_path: Path) -> List[DocumentChunk]:
        import csv
        chunks = []
        doc_id = file_path.stem
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                return []
            header = rows[0]
            # Chunk rows into groups of 10
            batch_size = 10
            for i in range(1, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                table_str = " | ".join(header) + "\n" + "\n".join([" | ".join(r) for r in batch])
                chunk_id = f"{doc_id}_batch_{i//batch_size+1}"
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=doc_id,
                        document_name=file_path.name,
                        document_type="csv",
                        page_number=1,
                        section_title=f"Data Table Rows {i}-{i+len(batch)-1}",
                        content=table_str,
                        metadata={"headers": header}
                    )
                )
        return chunks

    @staticmethod
    def _parse_text(file_path: Path) -> List[DocumentChunk]:
        text = file_path.read_text(encoding="utf-8")
        chunk_id = f"{file_path.stem}_all"
        return [
            DocumentChunk(
                chunk_id=chunk_id,
                document_id=file_path.stem,
                document_name=file_path.name,
                document_type="text",
                page_number=1,
                section_title="Full Document",
                content=text
            )
        ]
