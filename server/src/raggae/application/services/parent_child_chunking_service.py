class ParentChildChunkingService:
    """Splits text chunks into parent-child hierarchy.

    Parents are large chunks used for context.
    Children are smaller chunks used for precise vector search.
    """

    def split_into_parent_child(
        self,
        chunks: list[str],
        parent_size: int = 2000,
        child_size: int = 500,
        child_overlap: int = 50,
    ) -> list[tuple[str, list[str]]]:
        """Group chunks into parents and re-split each parent into children.

        Returns a list of (parent_text, [child_texts]) tuples.
        """
        if not chunks:
            return []

        non_empty = [c for c in chunks if c.strip()]
        if not non_empty:
            return []

        parents = self._group_into_parents(non_empty, parent_size)
        return [(parent, self._split_into_children(parent, child_size, child_overlap)) for parent in parents]

    def _group_into_parents(self, chunks: list[str], parent_size: int) -> list[str]:
        parents: list[str] = []
        current_parts: list[str] = []
        current_len = 0

        for chunk in chunks:
            chunk_len = len(chunk)
            separator_len = 2 if current_parts else 0  # "\n\n"
            if current_parts and current_len + separator_len + chunk_len > parent_size:
                parents.append("\n\n".join(current_parts))
                current_parts = [chunk]
                current_len = chunk_len
            else:
                current_parts.append(chunk)
                current_len += separator_len + chunk_len

        if current_parts:
            parents.append("\n\n".join(current_parts))

        return parents

    def _split_into_children(
        self, text: str, child_size: int, child_overlap: int
    ) -> list[str]:
        if len(text) <= child_size:
            return [text]

        children: list[str] = []
        step = child_size - child_overlap
        if step <= 0:
            step = 1

        pos = 0
        while pos < len(text):
            end = pos + child_size
            children.append(text[pos:end])
            if end >= len(text):
                break
            pos += step

        return children
