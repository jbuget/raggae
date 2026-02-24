from uuid import uuid4

import pytest
from raggae.infrastructure.services.minio_file_storage_service import MinioFileStorageService


class TestMinioFileStorageService:
    @pytest.mark.integration
    async def test_integration_upload_and_delete_file(self) -> None:
        minio = pytest.importorskip("minio")
        assert minio is not None

        bucket_name = f"raggae-test-{uuid4().hex[:8]}"
        storage_key = f"documents/{uuid4()}.txt"
        content = b"hello minio"
        content_type = "text/plain"

        try:
            service = MinioFileStorageService(
                endpoint="http://localhost:9000",
                access_key="minioadmin",
                secret_key="minioadmin",
                bucket_name=bucket_name,
                secure=False,
            )
        except Exception as exc:  # pragma: no cover - environment dependent
            pytest.skip(f"MinIO not available locally: {exc}")

        await service.upload_file(storage_key, content, content_type)
        await service.delete_file(storage_key)
