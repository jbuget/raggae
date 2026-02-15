from dataclasses import dataclass

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO


@dataclass
class QueryRelevantChunksResultDTO:
    chunks: list[RetrievedChunkDTO]
    strategy_used: str
    execution_time_ms: float
