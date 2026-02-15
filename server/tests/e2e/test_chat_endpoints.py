import json
from uuid import uuid4

from httpx import AsyncClient
from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.domain.exceptions.document_exceptions import LLMGenerationError


class TestChatEndpoints:
    async def _auth_headers(self, client: AsyncClient) -> dict[str, str]:
        unique = uuid4().hex
        email = f"{unique}@example.com"

        await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "SecurePass123!",
                "full_name": "Test User",
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": email,
                "password": "SecurePass123!",
            },
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    async def _create_project(self, client: AsyncClient) -> tuple[dict[str, str], str]:
        headers = await self._auth_headers(client)
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Project Chat"},
            headers=headers,
        )
        return headers, response.json()["id"]

    async def test_send_message_returns_200(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == project_id
        assert "conversation_id" in data
        assert data["message"] == "hello"
        assert isinstance(data["answer"], str)
        assert isinstance(data["chunks"], list)

    async def test_send_message_accepts_retrieval_strategy_and_filters(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        headers, project_id = await self._create_project(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={
                "message": "jwt token expiration",
                "limit": 3,
                "retrieval_strategy": "auto",
                "retrieval_filters": {"source_type": "paragraph"},
            },
            headers=headers,
        )

        # Then
        assert response.status_code == 200

    async def test_send_message_other_user_project_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        _, project_id = await self._create_project(client)
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404

    async def test_send_message_without_chunks_returns_fallback_answer(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        headers, project_id = await self._create_project(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "unknown question", "limit": 3},
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["chunks"] == []
        assert data["answer"] == "I could not find relevant context to answer your message."

    async def test_send_message_returns_422_when_llm_generation_fails(
        self,
        client: AsyncClient,
        monkeypatch,
    ) -> None:
        # Given
        from raggae.presentation.api import dependencies

        async def raise_llm_error(query: str, context_chunks: list[str]) -> str:
            del query, context_chunks
            raise LLMGenerationError("llm provider unavailable")

        monkeypatch.setattr(
            dependencies._llm_service,  # noqa: SLF001
            "generate_answer",
            raise_llm_error,
        )

        async def retrieve_one_chunk(  # type: ignore[no-untyped-def]
            project_id,
            query_text,
            query_embedding,
            limit,
            offset,
            min_score,
            strategy,
            metadata_filters,
        ):
            del (
                project_id,
                query_text,
                query_embedding,
                limit,
                offset,
                min_score,
                strategy,
                metadata_filters,
            )
            return [
                RetrievedChunkDTO(
                    chunk_id=uuid4(),
                    document_id=uuid4(),
                    content="chunk one",
                    score=0.99,
                )
            ]

        monkeypatch.setattr(
            dependencies._chunk_retrieval_service,  # noqa: SLF001
            "retrieve_chunks",
            retrieve_one_chunk,
        )
        headers, project_id = await self._create_project(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=headers,
        )

        # Then
        assert response.status_code == 422

    async def test_stream_message_returns_sse_events(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)

        # When
        async with client.stream(
            "POST",
            f"/api/v1/projects/{project_id}/chat/messages/stream",
            json={"message": "hello", "limit": 3},
            headers=headers,
        ) as response:
            payload = ""
            async for chunk in response.aiter_text():
                payload += chunk

        # Then
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        assert "data:" in payload
        data_events = [
            line.removeprefix("data: ").strip()
            for line in payload.splitlines()
            if line.startswith("data: ")
        ]
        parsed_events = [json.loads(raw) for raw in data_events]
        done_events = [event for event in parsed_events if event.get("done") is True]
        assert len(done_events) == 1
        assert "conversation_id" in done_events[0]
        assert isinstance(done_events[0]["chunks"], list)
        if done_events[0]["chunks"]:
            first_chunk = done_events[0]["chunks"][0]
            assert "content" in first_chunk
            assert "document_file_name" in first_chunk

    async def test_stream_message_other_user_project_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        _, project_id = await self._create_project(client)
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages/stream",
            json={"message": "hello", "limit": 3},
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404

    async def test_list_conversation_messages_returns_200(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)
        send_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=headers,
        )
        conversation_id = send_response.json()["conversation_id"]

        # When
        response = await client.get(
            f"/api/v1/projects/{project_id}/chat/conversations/{conversation_id}/messages",
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) >= 2
        assert payload[0]["role"] == "user"
        assert payload[0]["source_documents"] is None
        assert payload[0]["reliability_percent"] is None
        assert payload[1]["role"] == "assistant"
        assert isinstance(payload[1]["source_documents"], list)
        assert isinstance(payload[1]["reliability_percent"], int)

    async def test_list_conversation_messages_supports_pagination(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        headers, project_id = await self._create_project(client)
        send_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=headers,
        )
        conversation_id = send_response.json()["conversation_id"]

        # When
        response = await client.get(
            f"/api/v1/projects/{project_id}/chat/conversations/{conversation_id}/messages"
            "?limit=1&offset=1",
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 1
        assert payload[0]["role"] == "assistant"

    async def test_list_conversation_messages_other_user_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        owner_headers, project_id = await self._create_project(client)
        send_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=owner_headers,
        )
        conversation_id = send_response.json()["conversation_id"]
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.get(
            f"/api/v1/projects/{project_id}/chat/conversations/{conversation_id}/messages",
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404

    async def test_list_conversations_returns_200(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)
        await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=headers,
        )

        # When
        response = await client.get(
            f"/api/v1/projects/{project_id}/chat/conversations",
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) >= 1
        assert payload[0]["project_id"] == project_id
        assert "title" in payload[0]
        assert payload[0]["title"] is not None
        assert payload[0]["title"].strip() != ""

    async def test_list_conversations_supports_pagination(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        headers, project_id = await self._create_project(client)
        await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "first", "limit": 3},
            headers=headers,
        )
        await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "second", "limit": 3},
            headers=headers,
        )

        # When
        response = await client.get(
            f"/api/v1/projects/{project_id}/chat/conversations?limit=1&offset=0",
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 1

    async def test_list_conversations_other_user_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        _, project_id = await self._create_project(client)
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.get(
            f"/api/v1/projects/{project_id}/chat/conversations",
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404

    async def test_get_conversation_returns_200(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)
        send_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=headers,
        )
        conversation_id = send_response.json()["conversation_id"]

        # When
        response = await client.get(
            f"/api/v1/projects/{project_id}/chat/conversations/{conversation_id}",
            headers=headers,
        )

        # Then
        assert response.status_code == 200
        payload = response.json()
        assert payload["id"] == conversation_id
        assert payload["message_count"] >= 2
        assert "title" in payload
        assert payload["last_message"] is not None

    async def test_get_conversation_other_user_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        owner_headers, project_id = await self._create_project(client)
        send_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=owner_headers,
        )
        conversation_id = send_response.json()["conversation_id"]
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.get(
            f"/api/v1/projects/{project_id}/chat/conversations/{conversation_id}",
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404

    async def test_delete_conversation_returns_204(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)
        send_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=headers,
        )
        conversation_id = send_response.json()["conversation_id"]

        # When
        response = await client.delete(
            f"/api/v1/projects/{project_id}/chat/conversations/{conversation_id}",
            headers=headers,
        )

        # Then
        assert response.status_code == 204

    async def test_delete_conversation_other_user_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        owner_headers, project_id = await self._create_project(client)
        send_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=owner_headers,
        )
        conversation_id = send_response.json()["conversation_id"]
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.delete(
            f"/api/v1/projects/{project_id}/chat/conversations/{conversation_id}",
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404

    async def test_update_conversation_returns_204(self, client: AsyncClient) -> None:
        # Given
        headers, project_id = await self._create_project(client)
        send_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=headers,
        )
        conversation_id = send_response.json()["conversation_id"]

        # When
        response = await client.patch(
            f"/api/v1/projects/{project_id}/chat/conversations/{conversation_id}",
            json={"title": "My chat"},
            headers=headers,
        )

        # Then
        assert response.status_code == 204

    async def test_update_conversation_other_user_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        owner_headers, project_id = await self._create_project(client)
        send_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=owner_headers,
        )
        conversation_id = send_response.json()["conversation_id"]
        other_user_headers = await self._auth_headers(client)

        # When
        response = await client.patch(
            f"/api/v1/projects/{project_id}/chat/conversations/{conversation_id}",
            json={"title": "My chat"},
            headers=other_user_headers,
        )

        # Then
        assert response.status_code == 404

    async def test_send_message_with_existing_conversation_id_reuses_conversation(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        headers, project_id = await self._create_project(client)
        first_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=headers,
        )
        conversation_id = first_response.json()["conversation_id"]

        # When
        second_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={
                "message": "hello again",
                "limit": 3,
                "conversation_id": conversation_id,
            },
            headers=headers,
        )

        # Then
        assert second_response.status_code == 200
        assert second_response.json()["conversation_id"] == conversation_id

    async def test_send_message_without_conversation_id_creates_new_conversation_each_time(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        headers, project_id = await self._create_project(client)

        # When
        first_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "First", "limit": 3},
            headers=headers,
        )
        second_response = await client.post(
            f"/api/v1/projects/{project_id}/chat/messages",
            json={"message": "Second", "limit": 3},
            headers=headers,
        )

        # Then
        assert first_response.status_code == 200
        assert second_response.status_code == 200
        assert first_response.json()["conversation_id"] != second_response.json()["conversation_id"]

    async def test_send_message_with_foreign_conversation_id_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        # Given
        owner_headers, owner_project_id = await self._create_project(client)
        owner_send = await client.post(
            f"/api/v1/projects/{owner_project_id}/chat/messages",
            json={"message": "hello", "limit": 3},
            headers=owner_headers,
        )
        foreign_conversation_id = owner_send.json()["conversation_id"]
        other_headers, other_project_id = await self._create_project(client)

        # When
        response = await client.post(
            f"/api/v1/projects/{other_project_id}/chat/messages",
            json={
                "message": "hello",
                "limit": 3,
                "conversation_id": foreign_conversation_id,
            },
            headers=other_headers,
        )

        # Then
        assert response.status_code == 404
