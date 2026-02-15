from uuid import UUID

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.services.chunk_retrieval_service import ChunkRetrievalService
from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class QueryRelevantChunks:
    """Use Case: Retrieve relevant chunks for a user query within a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        embedding_service: EmbeddingService,
        chunk_retrieval_service: ChunkRetrievalService,
        min_score: float = 0.0,
    ) -> None:
        self._project_repository = project_repository
        self._embedding_service = embedding_service
        self._chunk_retrieval_service = chunk_retrieval_service
        self._min_score = min_score

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        query: str,
        limit: int = 5,
    ) -> list[RetrievedChunkDTO]:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        query_embedding = (await self._embedding_service.embed_texts([query]))[0]
        chunks = await self._chunk_retrieval_service.retrieve_chunks(
            project_id=project_id,
            query_embedding=query_embedding,
            limit=limit,
            min_score=self._min_score,
        )
        return [chunk for chunk in chunks if chunk.score >= self._min_score]
