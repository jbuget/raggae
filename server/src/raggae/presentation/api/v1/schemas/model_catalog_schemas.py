from pydantic import BaseModel


class ModelEntry(BaseModel):
    id: str
    label: str


class ModelCatalogResponse(BaseModel):
    embedding: dict[str, list[ModelEntry]]
    llm: dict[str, list[ModelEntry]]
    reranker: dict[str, list[ModelEntry]]
