import pytest

from raggae.domain.value_objects.document_status import DocumentStatus


class TestDocumentStatus:
    def test_has_uploaded_value(self) -> None:
        assert DocumentStatus.UPLOADED == "uploaded"

    def test_has_processing_value(self) -> None:
        assert DocumentStatus.PROCESSING == "processing"

    def test_has_indexed_value(self) -> None:
        assert DocumentStatus.INDEXED == "indexed"

    def test_has_error_value(self) -> None:
        assert DocumentStatus.ERROR == "error"

    def test_has_exactly_four_members(self) -> None:
        assert len(DocumentStatus) == 4

    def test_can_be_created_from_string(self) -> None:
        assert DocumentStatus("uploaded") is DocumentStatus.UPLOADED

    def test_invalid_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            DocumentStatus("invalid")
