"""Tests for SendMessage._extract_source_documents."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.application.use_cases.chat.send_message import SendMessage
from raggae.domain.entities.conversation import Conversation
from raggae.domain.entities.project import Project


def _make_use_case() -> SendMessage:
    conversation_repository = AsyncMock()
    conversation_repository.find_by_project_and_user.return_value = []
    conversation_repository.create.return_value = Conversation(
        id=uuid4(),
        project_id=uuid4(),
        user_id=uuid4(),
        created_at=datetime.now(UTC),
    )
    message_repository = AsyncMock()
    message_repository.count_by_conversation_id.return_value = 0
    message_repository.find_by_conversation_id.return_value = []
    project_repository = AsyncMock()
    project_repository.find_by_id.return_value = Project(
        id=uuid4(),
        user_id=uuid4(),
        name="Project",
        description="",
        system_prompt="",
        is_published=False,
        created_at=datetime.now(UTC),
    )
    return SendMessage(
        query_relevant_chunks_use_case=AsyncMock(),
        llm_service=AsyncMock(),
        conversation_title_generator=AsyncMock(),
        project_repository=project_repository,
        conversation_repository=conversation_repository,
        message_repository=message_repository,
    )


class TestExtractSourceDocuments:
    def test_groups_chunk_ids_by_document(self) -> None:
        """Given chunks from the same document, chunk_ids should be grouped."""
        # Given
        doc_id = uuid4()
        chunk_a = uuid4()
        chunk_b = uuid4()
        chunks = [
            RetrievedChunkDTO(
                chunk_id=chunk_a,
                document_id=doc_id,
                content="a",
                score=0.9,
                document_file_name="doc.pdf",
            ),
            RetrievedChunkDTO(
                chunk_id=chunk_b,
                document_id=doc_id,
                content="b",
                score=0.8,
                document_file_name="doc.pdf",
            ),
        ]
        use_case = _make_use_case()

        # When
        result = use_case._extract_source_documents(chunks)

        # Then
        assert len(result) == 1
        assert result[0]["document_id"] == str(doc_id)
        assert result[0]["document_file_name"] == "doc.pdf"
        assert result[0]["chunk_ids"] == [str(chunk_a), str(chunk_b)]

    def test_multiple_documents_each_have_chunk_ids(self) -> None:
        """Given chunks from different documents, each should have its own chunk_ids."""
        # Given
        doc_a = uuid4()
        doc_b = uuid4()
        chunk_a = uuid4()
        chunk_b = uuid4()
        chunks = [
            RetrievedChunkDTO(
                chunk_id=chunk_a,
                document_id=doc_a,
                content="a",
                score=0.9,
                document_file_name="a.pdf",
            ),
            RetrievedChunkDTO(
                chunk_id=chunk_b,
                document_id=doc_b,
                content="b",
                score=0.8,
                document_file_name="b.pdf",
            ),
        ]
        use_case = _make_use_case()

        # When
        result = use_case._extract_source_documents(chunks)

        # Then
        assert len(result) == 2
        by_doc = {r["document_id"]: r for r in result}
        assert by_doc[str(doc_a)]["chunk_ids"] == [str(chunk_a)]
        assert by_doc[str(doc_b)]["chunk_ids"] == [str(chunk_b)]

    def test_empty_chunks_returns_empty_list(self) -> None:
        """Given no chunks, should return an empty list."""
        use_case = _make_use_case()
        assert use_case._extract_source_documents([]) == []

    def test_chunk_without_file_name_omits_key(self) -> None:
        """Given a chunk without document_file_name, the key should be absent."""
        # Given
        chunk_id = uuid4()
        doc_id = uuid4()
        chunks = [
            RetrievedChunkDTO(
                chunk_id=chunk_id,
                document_id=doc_id,
                content="a",
                score=0.9,
            ),
        ]
        use_case = _make_use_case()

        # When
        result = use_case._extract_source_documents(chunks)

        # Then
        assert len(result) == 1
        assert "document_file_name" not in result[0]
        assert result[0]["chunk_ids"] == [str(chunk_id)]
