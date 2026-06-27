"""OpenRouter chat client. Provider-agnostic: the model id comes from the env, so
swapping models needs no code change. Only this final reasoning step calls the
network — embeddings and reranking are local."""

import httpx
import structlog

from app.core.config import get_settings

log = structlog.get_logger()


class LLMError(RuntimeError):
    pass


class OpenRouterClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.openrouter_api_key
        self._model = model or settings.openrouter_model
        self._base_url = (base_url or settings.openrouter_base_url).rstrip("/")

    def complete_json(self, system: str, user: str, temperature: float = 0.2) -> str:
        """Send a chat completion requesting a JSON object; return the raw content."""
        return self._complete(system, user, temperature, json_object=True)

    def complete_text(self, system: str, user: str, temperature: float = 0.3) -> str:
        """Send a chat completion expecting free-form text (e.g. a HyDE passage)."""
        return self._complete(system, user, temperature, json_object=False)

    def _complete(
        self, system: str, user: str, temperature: float, json_object: bool
    ) -> str:
        if not self._api_key:
            raise LLMError("OPENROUTER_API_KEY is not set")

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        if json_object:
            payload["response_format"] = {"type": "json_object"}
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": "https://github.com/Khayal07/MemoryLens",
            "X-Title": "MemoryLens",
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    f"{self._base_url}/chat/completions", json=payload, headers=headers
                )
                resp.raise_for_status()
                data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as exc:
            log.error("llm.http_error", error=str(exc))
            raise LLMError(f"OpenRouter request failed: {exc}") from exc
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected OpenRouter response shape: {exc}") from exc
