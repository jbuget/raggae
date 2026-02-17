from dataclasses import replace
from datetime import UTC, datetime
import re
from uuid import uuid4

from raggae.application.interfaces.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from raggae.application.interfaces.services.chunking_strategy_selector import (
    ChunkingStrategySelector,
)
from raggae.application.interfaces.services.document_structure_analyzer import (
    DocumentStructureAnalyzer,
)
from raggae.application.interfaces.services.document_text_extractor import (
    DocumentTextExtractor,
)
from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.application.interfaces.services.text_chunker_service import TextChunkerService
from raggae.application.interfaces.services.text_sanitizer_service import (
    TextSanitizerService,
)
from raggae.application.services.chunking_strategy_selector import (
    DeterministicChunkingStrategySelector,
)
from raggae.domain.entities.document import Document
from raggae.domain.entities.document_chunk import DocumentChunk
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy

_PAGE_MARKER_RE = re.compile(r"\[\[PAGE:(\d+)\]\]")


class DocumentIndexingService:
    """Reusable service that runs the full indexing pipeline on a document."""

    def __init__(
        self,
        document_chunk_repository: DocumentChunkRepository,
        document_text_extractor: DocumentTextExtractor,
        text_sanitizer_service: TextSanitizerService,
        document_structure_analyzer: DocumentStructureAnalyzer,
        text_chunker_service: TextChunkerService,
        embedding_service: EmbeddingService,
        chunking_strategy_selector: ChunkingStrategySelector | None = None,
        chunker_backend: str = "native",
    ) -> None:
        self._document_chunk_repository = document_chunk_repository
        self._document_text_extractor = document_text_extractor
        self._text_sanitizer_service = text_sanitizer_service
        self._document_structure_analyzer = document_structure_analyzer
        self._text_chunker_service = text_chunker_service
        self._embedding_service = embedding_service
        self._chunking_strategy_selector: ChunkingStrategySelector
        if chunking_strategy_selector is None:
            self._chunking_strategy_selector = DeterministicChunkingStrategySelector()
        else:
            self._chunking_strategy_selector = chunking_strategy_selector
        self._chunker_backend = chunker_backend

    async def run_pipeline(self, document: Document, file_content: bytes) -> Document:
        extracted_text = await self._document_text_extractor.extract_text(
            file_name=document.file_name,
            content=file_content,
            content_type=document.content_type,
        )
        sanitized_text = await self._text_sanitizer_service.sanitize_text(extracted_text)

        if self._chunker_backend == "llamaindex":
            strategy = ChunkingStrategy.FIXED_WINDOW
        else:
            analysis = await self._document_structure_analyzer.analyze_text(sanitized_text)
            strategy = self._chunking_strategy_selector.select(
                has_headings=analysis.has_headings,
                paragraph_count=analysis.paragraph_count,
                average_paragraph_length=analysis.average_paragraph_length,
            )

        document = replace(document, processing_strategy=strategy)

        chunks = await self._text_chunker_service.chunk_text(sanitized_text, strategy=strategy)

        llamaindex_splitter = None
        if self._chunker_backend == "llamaindex":
            splitter_name = getattr(self._text_chunker_service, "last_splitter_name", None)
            if isinstance(splitter_name, str):
                llamaindex_splitter = splitter_name

        await self._document_chunk_repository.delete_by_document_id(document.id)

        if chunks:
            chunk_payloads = [self._build_chunk_payload(chunk_text) for chunk_text in chunks]
            indexed_payloads = [
                payload for payload in chunk_payloads if payload["content"].strip()
            ]
            if not indexed_payloads:
                return document

            chunk_contents = [str(payload["content"]) for payload in indexed_payloads]
            embeddings = await self._embedding_service.embed_texts(chunk_contents)
            document_chunks = [
                DocumentChunk(
                    id=uuid4(),
                    document_id=document.id,
                    chunk_index=index,
                    content=str(payload["content"]),
                    embedding=embeddings[index],
                    created_at=datetime.now(UTC),
                    metadata_json={
                        "metadata_version": 1,
                        "processing_strategy": strategy.value,
                        "source_type": strategy.value,
                        "chunker_backend": self._chunker_backend,
                        "llamaindex_splitter": llamaindex_splitter,
                        **(
                            {"pages": payload["pages"]}
                            if payload.get("pages") is not None
                            else {}
                        ),
                        **(
                            {"page_start": payload["page_start"]}
                            if payload.get("page_start") is not None
                            else {}
                        ),
                        **(
                            {"page_end": payload["page_end"]}
                            if payload.get("page_end") is not None
                            else {}
                        ),
                    },
                )
                for index, payload in enumerate(indexed_payloads)
            ]
            await self._document_chunk_repository.save_many(document_chunks)

        return document

    def _build_chunk_payload(self, chunk_text: str) -> dict[str, object]:
        pages = sorted({int(match) for match in _PAGE_MARKER_RE.findall(chunk_text)})
        content = _PAGE_MARKER_RE.sub("", chunk_text).strip()
        payload: dict[str, object] = {"content": content}
        if pages:
            payload["pages"] = pages
            payload["page_start"] = pages[0]
            payload["page_end"] = pages[-1]
        return payload
