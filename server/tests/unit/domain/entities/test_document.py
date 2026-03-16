from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.domain.entities.document import Document
from raggae.domain.exceptions.document_exceptions import (
    InvalidDocumentStatusTransitionError,
)
from raggae.domain.value_objects.document_status import DocumentStatus


def _make_document(
    status: DocumentStatus = DocumentStatus.UPLOADED,
    error_message: str | None = None,
) -> Document:
    return Document(
        id=uuid4(),
        project_id=uuid4(),
        file_name="test.pdf",
        content_type="application/pdf",
        file_size=1024,
        storage_key="projects/123/documents/456-test.pdf",
        created_at=datetime.now(UTC),
        status=status,
        error_message=error_message,
    )


class TestDocumentStatus:
    def test_default_status_is_uploaded(self) -> None:
        doc = Document(
            id=uuid4(),
            project_id=uuid4(),
            file_name="test.pdf",
            content_type="application/pdf",
            file_size=1024,
            storage_key="key",
            created_at=datetime.now(UTC),
        )
        assert doc.status == DocumentStatus.UPLOADED
        assert doc.error_message is None


class TestDocumentTransitions:
    """Test all valid and invalid status transitions."""

    # --- Valid transitions ---

    def test_uploaded_to_processing(self) -> None:
        doc = _make_document(DocumentStatus.UPLOADED)
        result = doc.transition_to(DocumentStatus.PROCESSING)
        assert result.status == DocumentStatus.PROCESSING
        assert result.id == doc.id

    def test_processing_to_indexed(self) -> None:
        doc = _make_document(DocumentStatus.PROCESSING)
        result = doc.transition_to(DocumentStatus.INDEXED)
        assert result.status == DocumentStatus.INDEXED
        assert result.last_indexed_at is not None

    def test_processing_to_error(self) -> None:
        doc = _make_document(DocumentStatus.PROCESSING)
        result = doc.transition_to(DocumentStatus.ERROR, error_message="Extraction failed")
        assert result.status == DocumentStatus.ERROR
        assert result.error_message == "Extraction failed"

    def test_indexed_to_processing(self) -> None:
        doc = _make_document(DocumentStatus.INDEXED)
        result = doc.transition_to(DocumentStatus.PROCESSING)
        assert result.status == DocumentStatus.PROCESSING

    def test_error_to_processing(self) -> None:
        doc = _make_document(DocumentStatus.ERROR, error_message="Previous error")
        result = doc.transition_to(DocumentStatus.PROCESSING)
        assert result.status == DocumentStatus.PROCESSING
        assert result.error_message is None

    # --- Invalid transitions ---

    @pytest.mark.parametrize(
        ("from_status", "to_status"),
        [
            (DocumentStatus.UPLOADED, DocumentStatus.INDEXED),
            (DocumentStatus.UPLOADED, DocumentStatus.ERROR),
            (DocumentStatus.UPLOADED, DocumentStatus.UPLOADED),
            (DocumentStatus.PROCESSING, DocumentStatus.UPLOADED),
            (DocumentStatus.PROCESSING, DocumentStatus.PROCESSING),
            (DocumentStatus.INDEXED, DocumentStatus.UPLOADED),
            (DocumentStatus.INDEXED, DocumentStatus.ERROR),
            (DocumentStatus.INDEXED, DocumentStatus.INDEXED),
            (DocumentStatus.ERROR, DocumentStatus.UPLOADED),
            (DocumentStatus.ERROR, DocumentStatus.INDEXED),
            (DocumentStatus.ERROR, DocumentStatus.ERROR),
        ],
    )
    def test_invalid_transition_raises_error(
        self, from_status: DocumentStatus, to_status: DocumentStatus
    ) -> None:
        doc = _make_document(from_status)
        with pytest.raises(InvalidDocumentStatusTransitionError):
            doc.transition_to(to_status)

    def test_transition_to_error_without_message(self) -> None:
        doc = _make_document(DocumentStatus.PROCESSING)
        result = doc.transition_to(DocumentStatus.ERROR)
        assert result.status == DocumentStatus.ERROR
        assert result.error_message is None

    def test_transition_clears_error_message_when_leaving_error(self) -> None:
        doc = _make_document(DocumentStatus.ERROR, error_message="Old error")
        result = doc.transition_to(DocumentStatus.PROCESSING)
        assert result.error_message is None
