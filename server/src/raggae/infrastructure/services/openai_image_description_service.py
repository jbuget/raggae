import base64
import logging

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

_VISION_MODEL_PREFIXES = ("gpt-4o", "gpt-4-turbo", "gpt-4-vision")

_DESCRIPTION_PROMPT = (
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


class OpenAIImageDescriptionService:
    """Vision-based image description using OpenAI's multimodal models."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    def supports_vision(self) -> bool:
        return any(self._model.startswith(prefix) for prefix in _VISION_MODEL_PREFIXES)

    async def describe_image(self, image_bytes: bytes, content_type: str) -> str:
        b64 = base64.b64encode(image_bytes).decode()
        data_url = f"data:{content_type};base64,{b64}"
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": _DESCRIPTION_PROMPT},
                    ],
                }
            ],
        )
        return response.choices[0].message.content or ""
