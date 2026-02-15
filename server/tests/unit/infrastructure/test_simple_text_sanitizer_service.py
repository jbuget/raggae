from raggae.infrastructure.services.simple_text_sanitizer_service import (
    SimpleTextSanitizerService,
)


class TestSimpleTextSanitizerService:
    async def test_sanitize_text_normalizes_and_removes_control_chars(self) -> None:
        # Given
        service = SimpleTextSanitizerService()
        raw_text = "Line 1\x00\r\nLine 2\r\n\r\n\r\nLine 3\x07"

        # When
        result = await service.sanitize_text(raw_text)

        # Then
        assert result == "Line 1\nLine 2\n\nLine 3"

    async def test_sanitize_text_keeps_tabs_and_trim_edges(self) -> None:
        # Given
        service = SimpleTextSanitizerService()
        raw_text = "  \tItem 1\t  \nItem 2\t\t  \n"

        # When
        result = await service.sanitize_text(raw_text)

        # Then
        assert result == "Item 1\nItem 2"
