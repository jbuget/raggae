from raggae.application.services.parent_child_chunking_service import (
    ParentChildChunkingService,
)


class TestParentChildChunkingService:
    def test_groups_chunks_into_parents_and_keeps_originals_as_children(self) -> None:
        # Given
        service = ParentChildChunkingService()
        chunks = ["A" * 250, "B" * 250, "C" * 250, "D" * 250]

        # When
        result = service.split_into_parent_child(chunks, parent_size=600)

        # Then — 2 parents, each with 2 children (the original chunks)
        assert len(result) == 2
        parent_1, children_1 = result[0]
        parent_2, children_2 = result[1]
        assert parent_1 == "A" * 250 + "\n\n" + "B" * 250
        assert parent_2 == "C" * 250 + "\n\n" + "D" * 250
        assert children_1 == ["A" * 250, "B" * 250]
        assert children_2 == ["C" * 250, "D" * 250]

    def test_single_chunk_produces_one_parent_with_one_child(self) -> None:
        # Given
        service = ParentChildChunkingService()
        chunks = ["Hello world, this is a test."]

        # When
        result = service.split_into_parent_child(chunks, parent_size=2000)

        # Then
        assert len(result) == 1
        parent, children = result[0]
        assert parent == "Hello world, this is a test."
        assert children == ["Hello world, this is a test."]

    def test_large_chunk_stays_as_single_parent(self) -> None:
        # Given
        service = ParentChildChunkingService()
        text = "X" * 3000
        chunks = [text]

        # When
        result = service.split_into_parent_child(chunks, parent_size=2000)

        # Then — single chunk exceeds parent_size but forms one parent
        assert len(result) == 1
        parent, children = result[0]
        assert parent == text
        assert children == [text]

    def test_empty_chunks_returns_empty(self) -> None:
        # Given
        service = ParentChildChunkingService()

        # When
        result = service.split_into_parent_child([])

        # Then
        assert result == []

    def test_children_are_the_original_semantic_chunks(self) -> None:
        # Given — 3 semantic chunks of varying size
        service = ParentChildChunkingService()
        chunks = [
            "Introduction to the topic.",
            "Detailed explanation of the main concept with examples.",
            "Conclusion and summary.",
        ]

        # When
        result = service.split_into_parent_child(chunks, parent_size=2000)

        # Then — all fit in one parent, children are the originals
        assert len(result) == 1
        _, children = result[0]
        assert children == chunks

    def test_default_parameters(self) -> None:
        # Given
        service = ParentChildChunkingService()
        chunks = ["Word " * 500]  # 2500 chars

        # When
        result = service.split_into_parent_child(chunks)

        # Then — defaults: parent_size=10000
        assert len(result) == 1

    def test_whitespace_only_chunks_are_skipped(self) -> None:
        # Given
        service = ParentChildChunkingService()
        chunks = ["   ", "Hello"]

        # When
        result = service.split_into_parent_child(chunks, parent_size=2000)

        # Then
        assert len(result) == 1
        parent, children = result[0]
        assert parent == "Hello"
        assert children == ["Hello"]

    def test_many_small_chunks_grouped_correctly(self) -> None:
        # Given — 6 chunks of 100 chars each, parent_size=350
        service = ParentChildChunkingService()
        chunks = [f"chunk{i} " + "x" * 93 for i in range(6)]

        # When
        result = service.split_into_parent_child(chunks, parent_size=350)

        # Then — 3 chunks per parent (100+2+100+2+100=304 < 350)
        assert len(result) == 2
        _, children_1 = result[0]
        _, children_2 = result[1]
        assert len(children_1) == 3
        assert len(children_2) == 3
        assert children_1 == chunks[:3]
        assert children_2 == chunks[3:]
