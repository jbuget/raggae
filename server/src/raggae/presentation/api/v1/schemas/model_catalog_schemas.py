from pydantic import BaseModel


class ModelCatalogResponse(BaseModel):
    embedding: dict[str, list[str]]
    llm: dict[str, list[str]]
