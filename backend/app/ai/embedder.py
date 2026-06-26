"""Local sentence-transformers embedder. Free, runs in-process, no per-call cost.
The model is loaded lazily and cached so startup stays cheap and tests that don't
embed don't pay the import cost."""

from functools import lru_cache

from app.core.config import get_settings
from app.infra.models import EMBEDDING_DIM

# bge models recommend this instruction prefix on the *query* side only.
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


class SentenceTransformerEmbedder:
    dim = EMBEDDING_DIM

    def __init__(self, model_name: str) -> None:
        # Imported here so importing this module is cheap (torch is heavy).
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(
            texts, normalize_embeddings=True, convert_to_numpy=True
        )
        return [v.tolist() for v in vectors]

    def embed_query(self, text: str) -> list[float]:
        vector = self._model.encode(
            QUERY_INSTRUCTION + text, normalize_embeddings=True, convert_to_numpy=True
        )
        return vector.tolist()


@lru_cache
def get_embedder() -> SentenceTransformerEmbedder:
    return SentenceTransformerEmbedder(get_settings().embedding_model)
