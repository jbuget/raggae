from unittest.mock import AsyncMock

import pytest

from raggae.application.use_cases.project.generate_project_prompt import GenerateProjectPrompt


class TestGenerateProjectPrompt:
    @pytest.fixture
    def mock_llm_service(self) -> AsyncMock:
        service = AsyncMock()
        service.generate_answer.return_value = "You are a helpful HR assistant."
        return service

    @pytest.fixture
    def use_case(self, mock_llm_service: AsyncMock) -> GenerateProjectPrompt:
        return GenerateProjectPrompt(llm_service=mock_llm_service)

    async def test_returns_llm_output(
        self,
        use_case: GenerateProjectPrompt,
        mock_llm_service: AsyncMock,
    ) -> None:
        # When
        result = await use_case.execute(description="Answer HR questions about leave policies")

        # Then
        assert result == "You are a helpful HR assistant."
        mock_llm_service.generate_answer.assert_called_once()

    async def test_description_is_included_in_prompt(
        self,
        use_case: GenerateProjectPrompt,
        mock_llm_service: AsyncMock,
    ) -> None:
        # When
        await use_case.execute(description="Answer questions about accounting")

        # Then
        prompt_sent = mock_llm_service.generate_answer.call_args[0][0]
        assert "Answer questions about accounting" in prompt_sent

    async def test_name_is_included_in_prompt_when_provided(
        self,
        use_case: GenerateProjectPrompt,
        mock_llm_service: AsyncMock,
    ) -> None:
        # When
        await use_case.execute(description="Answer HR questions", name="HR Assistant")

        # Then
        prompt_sent = mock_llm_service.generate_answer.call_args[0][0]
        assert "HR Assistant" in prompt_sent

    async def test_name_is_omitted_from_prompt_when_empty(
        self,
        use_case: GenerateProjectPrompt,
        mock_llm_service: AsyncMock,
    ) -> None:
        # When
        await use_case.execute(description="Answer HR questions", name="")

        # Then
        prompt_sent = mock_llm_service.generate_answer.call_args[0][0]
        assert "Assistant name:" not in prompt_sent

    async def test_audience_is_included_in_prompt_when_provided(
        self,
        use_case: GenerateProjectPrompt,
        mock_llm_service: AsyncMock,
    ) -> None:
        # When
        await use_case.execute(
            description="Answer HR questions",
            audience="Company employees",
        )

        # Then
        prompt_sent = mock_llm_service.generate_answer.call_args[0][0]
        assert "Company employees" in prompt_sent

    async def test_audience_is_omitted_from_prompt_when_empty(
        self,
        use_case: GenerateProjectPrompt,
        mock_llm_service: AsyncMock,
    ) -> None:
        # When
        await use_case.execute(description="Answer HR questions", audience="")

        # Then
        prompt_sent = mock_llm_service.generate_answer.call_args[0][0]
        assert "Target audience:" not in prompt_sent

    async def test_all_optional_fields_combined(
        self,
        use_case: GenerateProjectPrompt,
        mock_llm_service: AsyncMock,
    ) -> None:
        # When
        await use_case.execute(
            description="Answer legal questions",
            name="Legal Bot",
            audience="Lawyers",
        )

        # Then
        prompt_sent = mock_llm_service.generate_answer.call_args[0][0]
        assert "Answer legal questions" in prompt_sent
        assert "Legal Bot" in prompt_sent
        assert "Lawyers" in prompt_sent

    async def test_propagates_llm_exception(
        self,
        use_case: GenerateProjectPrompt,
        mock_llm_service: AsyncMock,
    ) -> None:
        # Given
        mock_llm_service.generate_answer.side_effect = RuntimeError("LLM unavailable")

        # When / Then
        with pytest.raises(RuntimeError, match="LLM unavailable"):
            await use_case.execute(description="Answer HR questions")
