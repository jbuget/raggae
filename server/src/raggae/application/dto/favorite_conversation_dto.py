from dataclasses import dataclass

from raggae.domain.entities.conversation import Conversation


@dataclass
class FavoriteConversationResult:
    """Résultat enrichi d'une conversation favorite avec le nom du projet associé."""

    conversation: Conversation
    project_name: str
