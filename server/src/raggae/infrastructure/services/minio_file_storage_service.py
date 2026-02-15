class MinioFileStorageService:
    """MinIO implementation for S3-compatible object storage."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool,
    ) -> None:
        try:
            from minio import Minio
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "minio package is required for MinioFileStorageService. "
                "Install dependencies with `pip install -e .[dev]`."
            ) from exc

        self._client = Minio(
            endpoint.replace("http://", "").replace("https://", ""),
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self._bucket_name = bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        if not self._client.bucket_exists(self._bucket_name):
            self._client.make_bucket(self._bucket_name)

    async def upload_file(self, storage_key: str, content: bytes, content_type: str) -> None:
        from io import BytesIO

        self._client.put_object(
            bucket_name=self._bucket_name,
            object_name=storage_key,
            data=BytesIO(content),
            length=len(content),
            content_type=content_type,
        )

    async def download_file(self, storage_key: str) -> tuple[bytes, str]:
        response = self._client.get_object(
            bucket_name=self._bucket_name,
            object_name=storage_key,
        )
        try:
            data = response.read()
            content_type = response.headers.get("Content-Type", "application/octet-stream")
            return data, content_type
        finally:
            response.close()
            response.release_conn()

    async def delete_file(self, storage_key: str) -> None:
        self._client.remove_object(
            bucket_name=self._bucket_name,
            object_name=storage_key,
        )
