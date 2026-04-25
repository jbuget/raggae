from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from raggae.application.dto.stats_dto import (
    StatsDTO,
    StatsFonctionnementDTO,
    StatsImpactDTO,
    StatsUsageDTO,
)
from raggae.application.interfaces.repositories.stats_repository import StatsRepository
from raggae.infrastructure.database.models.conversation_model import ConversationModel
from raggae.infrastructure.database.models.document_chunk_model import DocumentChunkModel
from raggae.infrastructure.database.models.document_model import DocumentModel
from raggae.infrastructure.database.models.message_model import MessageModel
from raggae.infrastructure.database.models.organization_model import OrganizationModel
from raggae.infrastructure.database.models.project_model import ProjectModel
from raggae.infrastructure.database.models.user_model import UserModel

_RELIABILITY_THRESHOLD = 70
_RELEVANCE_THRESHOLD = 50
_MULTI_TURN_MIN_USER_MESSAGES = 3


class SQLAlchemyStatsRepository(StatsRepository):
    """Compute platform-wide statistics via aggregated SQL queries."""

    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_stats(self) -> StatsDTO:
        async with self._session_factory() as session:
            fonctionnement = await self._get_fonctionnement(session)
            usage = await self._get_usage(session)
            impact = await self._get_impact(session)

        return StatsDTO(
            generated_at=datetime.now(UTC),
            north_star_reliable_answers=impact.reliable_answers_total,
            fonctionnement=fonctionnement,
            usage=usage,
            impact=impact,
        )

    async def _get_fonctionnement(self, session: AsyncSession) -> StatsFonctionnementDTO:
        total_docs = (await session.execute(select(func.count()).select_from(DocumentModel))).scalar_one()

        indexed_docs = (
            await session.execute(
                select(func.count()).select_from(DocumentModel).where(DocumentModel.status == "indexed")
            )
        ).scalar_one()

        indexing_rate = (indexed_docs / total_docs * 100.0) if total_docs > 0 else 0.0

        projects_with_docs = (
            await session.execute(
                select(func.count(func.distinct(DocumentModel.project_id))).where(
                    DocumentModel.status == "indexed"
                )
            )
        ).scalar_one()

        total_size_bytes = (
            await session.execute(select(func.coalesce(func.sum(DocumentModel.file_size), 0)))
        ).scalar_one()

        total_chunks = (
            await session.execute(select(func.count()).select_from(DocumentChunkModel))
        ).scalar_one()

        return StatsFonctionnementDTO(
            indexing_success_rate_percent=round(indexing_rate, 1),
            projects_with_documents=int(projects_with_docs),
            total_document_size_mb=round(float(total_size_bytes) / (1024 * 1024), 1),
            total_chunks=int(total_chunks),
        )

    async def _get_usage(self, session: AsyncSession) -> StatsUsageDTO:
        users_total = (await session.execute(select(func.count()).select_from(UserModel))).scalar_one()

        cutoff_30d = datetime.now(UTC) - timedelta(days=30)
        users_active_30d = (
            await session.execute(
                select(func.count(func.distinct(ConversationModel.user_id)))
                .select_from(MessageModel)
                .join(ConversationModel, MessageModel.conversation_id == ConversationModel.id)
                .where(MessageModel.role == "user")
                .where(MessageModel.created_at >= cutoff_30d)
            )
        ).scalar_one()

        organizations_total = (
            await session.execute(select(func.count()).select_from(OrganizationModel))
        ).scalar_one()

        projects_total = (await session.execute(select(func.count()).select_from(ProjectModel))).scalar_one()

        projects_published = (
            await session.execute(
                select(func.count()).select_from(ProjectModel).where(ProjectModel.is_published.is_(True))
            )
        ).scalar_one()

        conversations_total = (
            await session.execute(select(func.count()).select_from(ConversationModel))
        ).scalar_one()

        messages_total = (
            await session.execute(
                select(func.count()).select_from(MessageModel).where(MessageModel.role == "user")
            )
        ).scalar_one()

        documents_total = (
            await session.execute(select(func.count()).select_from(DocumentModel))
        ).scalar_one()

        return StatsUsageDTO(
            users_total=int(users_total),
            users_active_30d=int(users_active_30d),
            organizations_total=int(organizations_total),
            projects_total=int(projects_total),
            projects_published=int(projects_published),
            conversations_total=int(conversations_total),
            messages_total=int(messages_total),
            documents_total=int(documents_total),
        )

    async def _get_impact(self, session: AsyncSession) -> StatsImpactDTO:
        reliable_answers = (
            await session.execute(
                select(func.count())
                .select_from(MessageModel)
                .where(MessageModel.role == "assistant")
                .where(MessageModel.reliability_percent >= _RELIABILITY_THRESHOLD)
            )
        ).scalar_one()

        avg_reliability = (
            await session.execute(
                select(func.avg(MessageModel.reliability_percent))
                .where(MessageModel.role == "assistant")
                .where(MessageModel.reliability_percent.isnot(None))
            )
        ).scalar_one()

        total_assistant = (
            await session.execute(
                select(func.count())
                .select_from(MessageModel)
                .where(MessageModel.role == "assistant")
                .where(MessageModel.reliability_percent.isnot(None))
            )
        ).scalar_one()

        relevant_answers = (
            await session.execute(
                select(func.count())
                .select_from(MessageModel)
                .where(MessageModel.role == "assistant")
                .where(MessageModel.reliability_percent >= _RELEVANCE_THRESHOLD)
            )
        ).scalar_one()

        relevant_rate = (relevant_answers / total_assistant * 100.0) if total_assistant > 0 else 0.0

        # Multi-turn: conversations with >= 3 user messages
        multi_turn_subq = (
            select(MessageModel.conversation_id)
            .where(MessageModel.role == "user")
            .group_by(MessageModel.conversation_id)
            .having(func.count() >= _MULTI_TURN_MIN_USER_MESSAGES)
            .subquery()
        )
        multi_turn_count = (
            await session.execute(select(func.count()).select_from(multi_turn_subq))
        ).scalar_one()

        conversations_total = (
            await session.execute(select(func.count()).select_from(ConversationModel))
        ).scalar_one()

        multi_turn_rate = (multi_turn_count / conversations_total * 100.0) if conversations_total > 0 else 0.0

        # Average sources per answer (JSONB array length)
        avg_sources_row = (
            await session.execute(
                text(
                    "SELECT AVG(jsonb_array_length(source_documents)) "
                    "FROM messages "
                    "WHERE role = 'assistant' "
                    "AND source_documents IS NOT NULL "
                    "AND jsonb_array_length(source_documents) > 0"
                )
            )
        ).scalar_one()

        return StatsImpactDTO(
            reliable_answers_total=int(reliable_answers),
            average_reliability_percent=round(float(avg_reliability or 0), 1),
            relevant_answers_rate_percent=round(relevant_rate, 1),
            multi_turn_conversations_rate_percent=round(multi_turn_rate, 1),
            average_sources_per_answer=round(float(avg_sources_row or 0), 1),
        )
