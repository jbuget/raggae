from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.application.use_cases.chat.send_message import SendMessage
from raggae.domain.entities.conversation import Conversation
from raggae.domain.entities.message import Message
from raggae.domain.entities.project import Project


class TestSendMessagePersistence:
    async def test_send_message_persists_user_and_assistant_messages(self) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        conversation = Conversation(
            id=uuid4(),
            project_id=project_id,
            user_id=user_id,
            created_at=datetime.now(UTC),
        )
        query_use_case = AsyncMock()
        query_use_case.execute.return_value = [
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="chunk one",
                score=0.91,
            )
        ]
        llm_service = AsyncMock()
        llm_service.generate_answer.return_value = "assistant answer"
        title_generator = AsyncMock()
        title_generator.generate_title.return_value = "Generated title"
        project_repository = AsyncMock()
        project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="project prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        conversation_repository = AsyncMock()
        conversation_repository.find_by_project_and_user.return_value = []
        conversation_repository.create.return_value = conversation
        message_repository = AsyncMock()

        use_case = SendMessage(
            query_relevant_chunks_use_case=query_use_case,
            llm_service=llm_service,
            conversation_title_generator=title_generator,
            project_repository=project_repository,
            conversation_repository=conversation_repository,
            message_repository=message_repository,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            message="hello",
            limit=3,
        )

        # Then
        conversation_repository.create.assert_awaited_once_with(
            project_id=project_id,
            user_id=user_id,
        )
        title_generator.generate_title.assert_awaited_once_with(
            user_message="hello",
            assistant_answer="assistant answer",
        )
        conversation_repository.update_title.assert_awaited_once_with(
            conversation.id,
            "Generated title",
        )
        assert message_repository.save.call_count == 2
        first_saved = message_repository.save.call_args_list[0].args[0]
        second_saved = message_repository.save.call_args_list[1].args[0]
        assert first_saved.role == "user"
        assert second_saved.role == "assistant"
        assert second_saved.source_documents is not None
        assert len(second_saved.source_documents) == 1
        assert second_saved.reliability_percent is not None
        assert 0 <= second_saved.reliability_percent <= 100
        assert result.conversation_id == conversation.id

    async def test_send_message_with_existing_conversation_id_uses_it(self) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        conversation = Conversation(
            id=uuid4(),
            project_id=project_id,
            user_id=user_id,
            created_at=datetime.now(UTC),
        )
        query_use_case = AsyncMock()
        query_use_case.execute.return_value = []
        llm_service = AsyncMock()
        title_generator = AsyncMock()
        project_repository = AsyncMock()
        project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="project prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        conversation_repository = AsyncMock()
        conversation_repository.find_by_id.return_value = conversation
        message_repository = AsyncMock()
        use_case = SendMessage(
            query_relevant_chunks_use_case=query_use_case,
            llm_service=llm_service,
            conversation_title_generator=title_generator,
            project_repository=project_repository,
            conversation_repository=conversation_repository,
            message_repository=message_repository,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            message="hello",
            limit=3,
            conversation_id=conversation.id,
        )

        # Then
        conversation_repository.find_by_id.assert_awaited_once_with(conversation.id)
        conversation_repository.create.assert_not_called()
        title_generator.generate_title.assert_not_called()
        conversation_repository.update_title.assert_not_called()
        assert result.conversation_id == conversation.id

    @pytest.mark.parametrize(
        ("generated_title", "expected_title"),
        [
            ("   ", "hello there"),
            (
                "A very long title generated by llm that should be trimmed "
                "at some point beyond the limit",
                "A very long title generated by llm that should be trimmed at some point beyond t",
            ),
        ],
    )
    async def test_send_message_new_conversation_uses_fallback_title_when_invalid_generated_title(
        self,
        generated_title: str,
        expected_title: str,
    ) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        conversation = Conversation(
            id=uuid4(),
            project_id=project_id,
            user_id=user_id,
            created_at=datetime.now(UTC),
        )
        query_use_case = AsyncMock()
        query_use_case.execute.return_value = []
        llm_service = AsyncMock()
        title_generator = AsyncMock()
        title_generator.generate_title.return_value = generated_title
        project_repository = AsyncMock()
        project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="project prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        conversation_repository = AsyncMock()
        conversation_repository.find_by_project_and_user.return_value = []
        conversation_repository.create.return_value = conversation
        message_repository = AsyncMock()
        use_case = SendMessage(
            query_relevant_chunks_use_case=query_use_case,
            llm_service=llm_service,
            conversation_title_generator=title_generator,
            project_repository=project_repository,
            conversation_repository=conversation_repository,
            message_repository=message_repository,
        )

        # When
        await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            message="hello there",
            limit=3,
        )

        # Then
        conversation_repository.update_title.assert_awaited_once_with(
            conversation.id,
            expected_title,
        )

    async def test_send_message_new_conversation_uses_fallback_title_when_generation_fails(
        self,
    ) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        conversation = Conversation(
            id=uuid4(),
            project_id=project_id,
            user_id=user_id,
            created_at=datetime.now(UTC),
        )
        query_use_case = AsyncMock()
        query_use_case.execute.return_value = []
        llm_service = AsyncMock()
        title_generator = AsyncMock()
        title_generator.generate_title.side_effect = RuntimeError("LLM down")
        project_repository = AsyncMock()
        project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="project prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        conversation_repository = AsyncMock()
        conversation_repository.find_by_project_and_user.return_value = []
        conversation_repository.create.return_value = conversation
        message_repository = AsyncMock()
        use_case = SendMessage(
            query_relevant_chunks_use_case=query_use_case,
            llm_service=llm_service,
            conversation_title_generator=title_generator,
            project_repository=project_repository,
            conversation_repository=conversation_repository,
            message_repository=message_repository,
        )

        # When
        await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            message="hello there",
            limit=3,
        )

        # Then
        conversation_repository.update_title.assert_awaited_once_with(
            conversation.id,
            "hello there",
        )

    async def test_send_message_reuses_pending_conversation_without_duplicate_user_message(
        self,
    ) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        conversation = Conversation(
            id=uuid4(),
            project_id=project_id,
            user_id=user_id,
            created_at=datetime.now(UTC),
        )
        query_use_case = AsyncMock()
        query_use_case.execute.return_value = [
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="chunk one",
                score=0.9,
            )
        ]
        llm_service = AsyncMock()
        llm_service.generate_answer.return_value = "assistant answer"
        title_generator = AsyncMock()
        title_generator.generate_title.return_value = "Generated title"
        project_repository = AsyncMock()
        project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="project prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        conversation_repository = AsyncMock()
        conversation_repository.find_by_project_and_user.return_value = [conversation]
        message_repository = AsyncMock()
        message_repository.find_latest_by_conversation_id.return_value = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role="user",
            content="hello",
            created_at=datetime.now(UTC),
        )

        use_case = SendMessage(
            query_relevant_chunks_use_case=query_use_case,
            llm_service=llm_service,
            conversation_title_generator=title_generator,
            project_repository=project_repository,
            conversation_repository=conversation_repository,
            message_repository=message_repository,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            message="hello",
            limit=3,
        )

        # Then
        conversation_repository.create.assert_not_called()
        assert message_repository.save.call_count == 1
        saved = message_repository.save.call_args_list[0].args[0]
        assert saved.role == "assistant"
        assert result.conversation_id == conversation.id
