from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.application.use_cases.chat.send_message import SendMessage
from raggae.domain.entities.conversation import Conversation
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class TestSendMessage:
    @pytest.fixture
    def mock_query_relevant_chunks(self) -> AsyncMock:
        use_case = AsyncMock()
        use_case.execute.return_value = [
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="chunk one",
                score=0.9,
            ),
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="chunk two",
                score=0.8,
            ),
        ]
        return use_case

    @pytest.fixture
    def mock_llm_service(self) -> AsyncMock:
        llm = AsyncMock()
        llm.generate_answer.return_value = "answer"
        return llm

    @pytest.fixture
    def use_case(
        self,
        mock_query_relevant_chunks: AsyncMock,
        mock_llm_service: AsyncMock,
    ) -> SendMessage:
        conversation_repository = AsyncMock()
        conversation_repository.get_or_create.return_value = Conversation(
            id=uuid4(),
            project_id=uuid4(),
            user_id=uuid4(),
            created_at=datetime.now(UTC),
        )
        message_repository = AsyncMock()
        title_generator = AsyncMock()
        title_generator.generate_title.return_value = "Generated title"
        return SendMessage(
            query_relevant_chunks_use_case=mock_query_relevant_chunks,
            llm_service=mock_llm_service,
            conversation_title_generator=title_generator,
            conversation_repository=conversation_repository,
            message_repository=message_repository,
        )

    async def test_send_message_success(
        self,
        use_case: SendMessage,
        mock_query_relevant_chunks: AsyncMock,
        mock_llm_service: AsyncMock,
    ) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            message="What is Raggae?",
            limit=2,
        )

        # Then
        mock_query_relevant_chunks.execute.assert_awaited_once_with(
            project_id=project_id,
            user_id=user_id,
            query="What is Raggae?",
            limit=2,
        )
        mock_llm_service.generate_answer.assert_awaited_once_with(
            query="What is Raggae?",
            context_chunks=["chunk one", "chunk two"],
        )
        assert result.answer == "answer"
        assert len(result.chunks) == 2

    async def test_send_message_project_not_found_bubbles_error(
        self,
        use_case: SendMessage,
        mock_query_relevant_chunks: AsyncMock,
    ) -> None:
        # Given
        mock_query_relevant_chunks.execute.side_effect = ProjectNotFoundError("not found")

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=uuid4(),
                user_id=uuid4(),
                message="hello",
                limit=3,
            )

    async def test_send_message_no_chunks_returns_fallback_without_calling_llm(
        self,
        use_case: SendMessage,
        mock_query_relevant_chunks: AsyncMock,
        mock_llm_service: AsyncMock,
    ) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        mock_query_relevant_chunks.execute.return_value = []

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            message="What is Raggae?",
            limit=2,
        )

        # Then
        mock_llm_service.generate_answer.assert_not_called()
        assert result.answer == "I could not find relevant context to answer your message."
        assert result.chunks == []
