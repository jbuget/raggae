from raggae.presentation.api.v1.schemas.chat_schemas import SendMessageRequest


class TestSendMessageRequest:
    def test_retrieval_filters_when_not_provided_defaults_to_none(self) -> None:
        # Given
        payload = {"message": "hello"}

        # When
        request = SendMessageRequest(**payload)

        # Then
        assert request.retrieval_filters is None

    def test_retrieval_filters_when_provided_uses_given_value(self) -> None:
        # Given
        payload = {"message": "hello", "retrieval_filters": {"source_type": "paragraph"}}

        # When
        request = SendMessageRequest(**payload)

        # Then
        assert request.retrieval_filters is not None
        assert request.retrieval_filters.source_type == "paragraph"
