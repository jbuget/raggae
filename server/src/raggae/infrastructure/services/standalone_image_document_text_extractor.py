import logging

from raggae.application.interfaces.services.image_description_service import ImageDescriptionService
from raggae.infrastructure.services.image_resizer_service import ImageResizerService

logger = logging.getLogger(__name__)

_VISION_PROMPT = (
    "Décris précisément le contenu de cette image pour permettre son indexation dans une base "
    "documentaire d'entreprise utilisée pour la recherche d'information (RAG).\n\n"
    "Inclure :\n"
    "- Le type de contenu (texte, schéma, graphique, tableau, photo, capture d'écran, etc.)\n"
    "- Tout le texte visible, transcrit fidèlement\n"
    "- Pour les schémas : les composants, relations et flux représentés\n"
    "- Pour les graphiques et tableaux : les données, axes et valeurs clés\n"
    "- Pour les photos : les éléments visuels pertinents dans un contexte professionnel\n\n"
    "Répondre uniquement avec la description, sans introduction ni conclusion."
)


class StandaloneImageDocumentTextExtractor:
    """Describe a standalone image file and produce an indexable text chunk."""

    def __init__(
        self,
        image_description_service: ImageDescriptionService,
        image_resizer_service: ImageResizerService,
    ) -> None:
        self._description_service = image_description_service
        self._resizer_service = image_resizer_service

    async def extract(self, image_bytes: bytes, content_type: str) -> str:
        if not self._description_service.supports_vision():
            logger.warning("vision_not_available_for_standalone_image")
            return ""

        resized = await self._resizer_service.resize_if_needed(image_bytes, content_type)
        description = await self._description_service.describe_image(resized, content_type)
        return f"[IMAGE]\n\n{description}"
