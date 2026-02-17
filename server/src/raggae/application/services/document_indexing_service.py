import logging
import re
from dataclasses import replace
from datetime import UTC, datetime
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
from raggae.application.interfaces.services.file_metadata_extractor import (
    FileMetadataExtractor,
)
from raggae.application.interfaces.services.keyword_extractor import KeywordExtractor
from raggae.application.interfaces.services.language_detector import LanguageDetector
from raggae.application.interfaces.services.text_chunker_service import TextChunkerService
from raggae.application.interfaces.services.text_sanitizer_service import (
    TextSanitizerService,
)
from raggae.application.services.chunking_strategy_selector import (
    DeterministicChunkingStrategySelector,
)
from raggae.application.services.parent_child_chunking_service import (
    ParentChildChunkingService,
)
from raggae.domain.entities.document import Document
from raggae.domain.entities.document_chunk import DocumentChunk
from raggae.domain.entities.project import Project
from raggae.domain.value_objects.chunk_level import ChunkLevel
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy

_PAGE_MARKER_RE = re.compile(r"\[\[PAGE:(\d+)\]\]")
logger = logging.getLogger(__name__)


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
        language_detector: LanguageDetector | None = None,
        keyword_extractor: KeywordExtractor | None = None,
        file_metadata_extractor: FileMetadataExtractor | None = None,
        chunking_strategy_selector: ChunkingStrategySelector | None = None,
        chunker_backend: str = "native",
        parent_child_chunking_service: ParentChildChunkingService | None = None,
    ) -> None:
        self._document_chunk_repository = document_chunk_repository
        self._document_text_extractor = document_text_extractor
        self._text_sanitizer_service = text_sanitizer_service
        self._document_structure_analyzer = document_structure_analyzer
        self._text_chunker_service = text_chunker_service
        self._embedding_service = embedding_service
        self._language_detector = language_detector
        self._keyword_extractor = keyword_extractor
        self._file_metadata_extractor = file_metadata_extractor
        self._chunking_strategy_selector: ChunkingStrategySelector
        if chunking_strategy_selector is None:
            self._chunking_strategy_selector = DeterministicChunkingStrategySelector()
        else:
            self._chunking_strategy_selector = chunking_strategy_selector
        self._chunker_backend = chunker_backend
        self._parent_child_chunking_service = parent_child_chunking_service

    async def run_pipeline(
        self,
        document: Document,
        project: Project,
        file_content: bytes,
    ) -> Document:
        extracted_text = await self._document_text_extractor.extract_text(
            file_name=document.file_name,
            content=file_content,
            content_type=document.content_type,
        )

        document = await self._enrich_document_metadata(
            document=document,
            extracted_text=extracted_text,
            file_content=file_content,
        )
        sanitized_text = await self._text_sanitizer_service.sanitize_text(extracted_text)
        document = await self._enrich_document_keywords(
            document=document,
            sanitized_text=sanitized_text,
        )

        strategy = project.chunking_strategy
        if strategy == ChunkingStrategy.AUTO:
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
            use_parent_child = (
                project.parent_child_chunking and self._parent_child_chunking_service is not None
            )

            if use_parent_child:
                document_chunks = await self._build_parent_child_chunks(
                    chunks=chunks,
                    document=document,
                    strategy=strategy,
                    llamaindex_splitter=llamaindex_splitter,
                )
            else:
                document_chunks = await self._build_standard_chunks(
                    chunks=chunks,
                    document=document,
                    strategy=strategy,
                    llamaindex_splitter=llamaindex_splitter,
                )

            if document_chunks:
                await self._document_chunk_repository.save_many(document_chunks)

        return document

    async def _build_standard_chunks(
        self,
        chunks: list[str],
        document: Document,
        strategy: ChunkingStrategy,
        llamaindex_splitter: str | None,
    ) -> list[DocumentChunk]:
        chunk_payloads = [self._build_chunk_payload(chunk_text) for chunk_text in chunks]
        indexed_payloads = [
            payload for payload in chunk_payloads if str(payload["content"]).strip()
        ]
        if not indexed_payloads:
            return []

        chunk_contents = [str(payload["content"]) for payload in indexed_payloads]
        embeddings = await self._embedding_service.embed_texts(chunk_contents)
        return [
            DocumentChunk(
                id=uuid4(),
                document_id=document.id,
                chunk_index=index,
                content=str(payload["content"]),
                embedding=embeddings[index],
                created_at=datetime.now(UTC),
                metadata_json=self._build_metadata(
                    strategy=strategy,
                    llamaindex_splitter=llamaindex_splitter,
                    payload=payload,
                ),
            )
            for index, payload in enumerate(indexed_payloads)
        ]

    async def _build_parent_child_chunks(
        self,
        chunks: list[str],
        document: Document,
        strategy: ChunkingStrategy,
        llamaindex_splitter: str | None,
    ) -> list[DocumentChunk]:
        assert self._parent_child_chunking_service is not None
        cleaned_chunks = [
            self._build_chunk_payload(c)["content"]
            for c in chunks
            if str(self._build_chunk_payload(c)["content"]).strip()
        ]
        if not cleaned_chunks:
            return []

        parent_children = self._parent_child_chunking_service.split_into_parent_child(
            [str(c) for c in cleaned_chunks]
        )

        all_document_chunks: list[DocumentChunk] = []
        all_child_texts: list[str] = []
        parent_child_map: list[tuple[int, int, int]] = []  # (parent_idx, child_start, child_end)

        for parent_idx, (_, children) in enumerate(parent_children):
            start = len(all_child_texts)
            all_child_texts.extend(children)
            end = len(all_child_texts)
            parent_child_map.append((parent_idx, start, end))

        embeddings = await self._embedding_service.embed_texts(all_child_texts)

        chunk_index = 0
        for parent_idx, (parent_text, _) in enumerate(parent_children):
            parent_id = uuid4()
            now = datetime.now(UTC)
            metadata = self._build_metadata(
                strategy=strategy,
                llamaindex_splitter=llamaindex_splitter,
                payload={"content": parent_text},
            )

            parent_chunk = DocumentChunk(
                id=parent_id,
                document_id=document.id,
                chunk_index=chunk_index,
                content=parent_text,
                embedding=[],
                created_at=now,
                metadata_json=metadata,
                chunk_level=ChunkLevel.PARENT,
            )
            all_document_chunks.append(parent_chunk)
            chunk_index += 1

            _, child_start, child_end = parent_child_map[parent_idx]
            for emb_idx in range(child_start, child_end):
                child_chunk = DocumentChunk(
                    id=uuid4(),
                    document_id=document.id,
                    chunk_index=chunk_index,
                    content=all_child_texts[emb_idx],
                    embedding=embeddings[emb_idx],
                    created_at=now,
                    metadata_json=metadata,
                    chunk_level=ChunkLevel.CHILD,
                    parent_chunk_id=parent_id,
                )
                all_document_chunks.append(child_chunk)
                chunk_index += 1

        return all_document_chunks

    def _build_chunk_payload(self, chunk_text: str) -> dict[str, object]:
        pages = sorted({int(match) for match in _PAGE_MARKER_RE.findall(chunk_text)})
        content = _PAGE_MARKER_RE.sub("", chunk_text).strip()
        payload: dict[str, object] = {"content": content}
        if pages:
            payload["pages"] = pages
            payload["page_start"] = pages[0]
            payload["page_end"] = pages[-1]
        return payload

    def _build_metadata(
        self,
        strategy: ChunkingStrategy,
        llamaindex_splitter: str | None,
        payload: dict[str, object],
    ) -> dict[str, object]:
        metadata: dict[str, object] = {
            "metadata_version": 1,
            "processing_strategy": strategy.value,
            "source_type": strategy.value,
            "chunker_backend": self._chunker_backend,
            "llamaindex_splitter": llamaindex_splitter,
        }
        if payload.get("pages") is not None:
            metadata["pages"] = payload["pages"]
        if payload.get("page_start") is not None:
            metadata["page_start"] = payload["page_start"]
        if payload.get("page_end") is not None:
            metadata["page_end"] = payload["page_end"]
        return metadata

    async def _enrich_document_metadata(
        self,
        document: Document,
        extracted_text: str,
        file_content: bytes,
    ) -> Document:
        updated = document

        if self._file_metadata_extractor is not None:
            try:
                file_metadata = await self._file_metadata_extractor.extract_metadata(
                    file_name=document.file_name,
                    content=file_content,
                    content_type=document.content_type,
                )
                updated = replace(
                    updated,
                    title=file_metadata.title,
                    authors=file_metadata.authors,
                    document_date=file_metadata.document_date,
                )
            except Exception:
                logger.warning("file_metadata_extraction_failed", exc_info=True)

        if self._language_detector is not None:
            try:
                language = await self._language_detector.detect_language(extracted_text)
                updated = replace(updated, language=language)
            except Exception:
                logger.warning("language_detection_failed", exc_info=True)

        return updated

    async def _enrich_document_keywords(self, document: Document, sanitized_text: str) -> Document:
        if self._keyword_extractor is None:
            return document
        try:
            keywords = await self._keyword_extractor.extract_keywords(sanitized_text)
            return replace(document, keywords=keywords or None)
        except Exception:
            logger.warning("keyword_extraction_failed", exc_info=True)
            return document
