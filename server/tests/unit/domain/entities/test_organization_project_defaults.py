from uuid import uuid4

from raggae.domain.entities.organization_project_defaults import OrganizationProjectDefaults


class TestOrganizationProjectDefaults:
    def test_create_minimal_should_have_all_none_fields(self) -> None:
        # Given / When
        org_id = uuid4()
        defaults = OrganizationProjectDefaults(organization_id=org_id)

        # Then
        assert defaults.organization_id == org_id
        assert defaults.embedding_backend is None
        assert defaults.embedding_model is None
        assert defaults.embedding_api_key_credential_id is None
        assert defaults.llm_backend is None
        assert defaults.llm_model is None
        assert defaults.llm_api_key_credential_id is None
        assert defaults.chunking_strategy is None
        assert defaults.parent_child_chunking is None
        assert defaults.retrieval_strategy is None
        assert defaults.retrieval_top_k is None
        assert defaults.retrieval_min_score is None
        assert defaults.reranking_enabled is None
        assert defaults.reranker_backend is None
        assert defaults.reranker_model is None
        assert defaults.reranker_candidate_multiplier is None
        assert defaults.chat_history_window_size is None
        assert defaults.chat_history_max_chars is None

    def test_has_models_defaults_when_no_fields_set_should_return_false(self) -> None:
        # Given
        defaults = OrganizationProjectDefaults(organization_id=uuid4())

        # When / Then
        assert defaults.has_models_defaults() is False

    def test_has_models_defaults_when_embedding_backend_set_should_return_true(self) -> None:
        # Given
        defaults = OrganizationProjectDefaults(organization_id=uuid4(), embedding_backend="openai")

        # When / Then
        assert defaults.has_models_defaults() is True

    def test_has_models_defaults_when_llm_backend_set_should_return_true(self) -> None:
        # Given
        defaults = OrganizationProjectDefaults(organization_id=uuid4(), llm_backend="anthropic")

        # When / Then
        assert defaults.has_models_defaults() is True

    def test_has_indexing_defaults_when_no_fields_set_should_return_false(self) -> None:
        # Given
        defaults = OrganizationProjectDefaults(organization_id=uuid4())

        # When / Then
        assert defaults.has_indexing_defaults() is False

    def test_has_indexing_defaults_when_chunking_strategy_set_should_return_true(self) -> None:
        # Given
        defaults = OrganizationProjectDefaults(organization_id=uuid4(), chunking_strategy="auto")

        # When / Then
        assert defaults.has_indexing_defaults() is True

    def test_has_retrieval_defaults_when_no_fields_set_should_return_false(self) -> None:
        # Given
        defaults = OrganizationProjectDefaults(organization_id=uuid4())

        # When / Then
        assert defaults.has_retrieval_defaults() is False

    def test_has_retrieval_defaults_when_top_k_set_should_return_true(self) -> None:
        # Given
        defaults = OrganizationProjectDefaults(organization_id=uuid4(), retrieval_top_k=10)

        # When / Then
        assert defaults.has_retrieval_defaults() is True

    def test_has_reranking_defaults_when_no_fields_set_should_return_false(self) -> None:
        # Given
        defaults = OrganizationProjectDefaults(organization_id=uuid4())

        # When / Then
        assert defaults.has_reranking_defaults() is False

    def test_has_reranking_defaults_when_reranking_enabled_set_should_return_true(self) -> None:
        # Given
        defaults = OrganizationProjectDefaults(organization_id=uuid4(), reranking_enabled=True)

        # When / Then
        assert defaults.has_reranking_defaults() is True

    def test_has_chat_history_defaults_when_no_fields_set_should_return_false(self) -> None:
        # Given
        defaults = OrganizationProjectDefaults(organization_id=uuid4())

        # When / Then
        assert defaults.has_chat_history_defaults() is False

    def test_has_chat_history_defaults_when_window_size_set_should_return_true(self) -> None:
        # Given
        defaults = OrganizationProjectDefaults(organization_id=uuid4(), chat_history_window_size=5)

        # When / Then
        assert defaults.has_chat_history_defaults() is True

    def test_is_immutable(self) -> None:
        # Given
        defaults = OrganizationProjectDefaults(organization_id=uuid4())

        # When / Then
        try:
            defaults.embedding_backend = "openai"  # type: ignore[misc]
            raise AssertionError("Should have raised FrozenInstanceError")
        except Exception:
            pass
