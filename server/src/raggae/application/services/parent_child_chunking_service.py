class ParentChildChunkingService:
    """Groups semantic chunks under larger parent chunks.

    Parents provide broad context for the LLM.
    Children (the original semantic chunks) are used for precise vector search.
    """

    def split_into_parent_child(
        self,
        chunks: list[str],
        parent_size: int = 2000,
    ) -> list[tuple[str, list[str]]]:
        """Group chunks into parents, keeping original chunks as children.

        Returns a list of (parent_text, [child_texts]) tuples.
        """
        if not chunks:
            return []

        non_empty = [c for c in chunks if c.strip()]
        if not non_empty:
            return []

        return self._group_into_parents(non_empty, parent_size)

    def _group_into_parents(
        self, chunks: list[str], parent_size: int
    ) -> list[tuple[str, list[str]]]:
        result: list[tuple[str, list[str]]] = []
        current_parts: list[str] = []
        current_len = 0

        for chunk in chunks:
            chunk_len = len(chunk)
            separator_len = 2 if current_parts else 0  # "\n\n"
            if current_parts and current_len + separator_len + chunk_len > parent_size:
                result.append(("\n\n".join(current_parts), list(current_parts)))
                current_parts = [chunk]
                current_len = chunk_len
            else:
                current_parts.append(chunk)
                current_len += separator_len + chunk_len

        if current_parts:
            result.append(("\n\n".join(current_parts), list(current_parts)))

        return result
