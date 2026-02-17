from raggae.application.services.parent_child_chunking_service import (
    ParentChildChunkingService,
)


class TestParentChildChunkingService:
    def test_split_into_parent_child_respects_sizes(self) -> None:
        # Given
        service = ParentChildChunkingService()
        chunks = ["A" * 250, "B" * 250, "C" * 250, "D" * 250]

        # When
        result = service.split_into_parent_child(
            chunks, parent_size=600, child_size=200, child_overlap=50
        )

        # Then — 2 parents expected (250+2+250=502 chars each, under 600)
        assert len(result) == 2
        parent_1, children_1 = result[0]
        parent_2, children_2 = result[1]
        assert parent_1 == "A" * 250 + "\n\n" + "B" * 250
        assert parent_2 == "C" * 250 + "\n\n" + "D" * 250
        assert len(children_1) >= 2
        assert len(children_2) >= 2
        for child in children_1 + children_2:
            assert len(child) <= 200 + 50  # child_size + overlap tolerance

    def test_single_chunk_produces_one_parent_with_children(self) -> None:
        # Given
        service = ParentChildChunkingService()
        chunks = ["Hello world, this is a test."]

        # When
        result = service.split_into_parent_child(
            chunks, parent_size=2000, child_size=500, child_overlap=50
        )

        # Then
        assert len(result) == 1
        parent, children = result[0]
        assert parent == "Hello world, this is a test."
        assert len(children) == 1
        assert children[0] == "Hello world, this is a test."

    def test_large_chunk_becomes_its_own_parent(self) -> None:
        # Given
        service = ParentChildChunkingService()
        text = "X" * 3000
        chunks = [text]

        # When
        result = service.split_into_parent_child(
            chunks, parent_size=2000, child_size=500, child_overlap=50
        )

        # Then — single large chunk becomes one parent, split into children
        assert len(result) == 1
        parent, children = result[0]
        assert parent == text
        assert len(children) >= 6  # 3000 / 500 = 6

    def test_empty_chunks_returns_empty(self) -> None:
        # Given
        service = ParentChildChunkingService()

        # When
        result = service.split_into_parent_child([])

        # Then
        assert result == []

    def test_children_have_overlap(self) -> None:
        # Given
        service = ParentChildChunkingService()
        text = "ABCDEFGHIJ" * 100  # 1000 chars

        # When
        result = service.split_into_parent_child(
            [text], parent_size=2000, child_size=200, child_overlap=50
        )

        # Then
        assert len(result) == 1
        _, children = result[0]
        assert len(children) >= 2
        # Verify overlap between consecutive children
        for i in range(len(children) - 1):
            suffix = children[i][-50:]
            prefix = children[i + 1][:50]
            assert suffix == prefix

    def test_default_parameters(self) -> None:
        # Given
        service = ParentChildChunkingService()
        chunks = ["Word " * 500]  # 2500 chars

        # When
        result = service.split_into_parent_child(chunks)

        # Then — defaults: parent_size=2000, child_size=500, child_overlap=50
        assert len(result) >= 1
        for _, children in result:
            for child in children:
                assert len(child) <= 550  # child_size + overlap

    def test_whitespace_only_chunks_are_skipped(self) -> None:
        # Given
        service = ParentChildChunkingService()
        chunks = ["   ", "Hello"]

        # When
        result = service.split_into_parent_child(chunks, parent_size=2000, child_size=500)

        # Then
        assert len(result) == 1
        parent, _ = result[0]
        assert parent == "Hello"
