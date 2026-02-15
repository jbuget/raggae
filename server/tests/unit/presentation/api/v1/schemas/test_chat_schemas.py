from raggae.presentation.api.v1.schemas.chat_schemas import SendMessageRequest


class TestSendMessageRequest:
    def test_retrieval_strategy_when_not_provided_defaults_to_none(self) -> None:
        # Given
        payload = {"message": "hello"}

        # When
        request = SendMessageRequest(**payload)

        # Then
        assert request.retrieval_strategy is None

    def test_retrieval_strategy_when_provided_uses_given_value(self) -> None:
        # Given
        payload = {"message": "hello", "retrieval_strategy": "vector"}

        # When
        request = SendMessageRequest(**payload)

        # Then
        assert request.retrieval_strategy == "vector"
