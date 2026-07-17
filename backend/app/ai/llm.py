"""LLM chat client. Provider-agnostic and OpenAI-compatible (/chat/completions).

Tries providers in order (OpenAI primary, OpenRouter fallback), so if OpenAI
credit runs out or errors, search keeps working on the free model. Model ids come
from env — swapping models needs no code change. Only this final reasoning step
calls the network; embeddings and reranking are local."""

from dataclasses import dataclass

import httpx
import structlog

from app.core.config import get_settings

log = structlog.get_logger()


class LLMError(RuntimeError):
    pass


@dataclass(frozen=True)
class _Provider:
    name: str
    api_key: str
    model: str
    base_url: str


class LLMClient:
    def __init__(self, providers: list[_Provider] | None = None) -> None:
        self._providers = providers if providers is not None else self._build_providers()

    @staticmethod
    def _build_providers() -> list[_Provider]:
        settings = get_settings()
        providers: list[_Provider] = []
        if settings.openai_api_key:
            providers.append(
                _Provider(
                    "openai",
                    settings.openai_api_key,
                    settings.openai_model,
                    settings.openai_base_url.rstrip("/"),
                )
            )
        if settings.openrouter_api_key and (settings.llm_fallback_enabled or not providers):
            providers.append(
                _Provider(
                    "openrouter",
                    settings.openrouter_api_key,
                    settings.openrouter_model,
                    settings.openrouter_base_url.rstrip("/"),
                )
            )
        return providers

    def complete_json(
        self, system: str, user: str, temperature: float = 0.2, model: str | None = None
    ) -> str:
        """Send a chat completion requesting a JSON object; return the raw content.
        `model` overrides the primary (OpenAI) provider's model for this one call —
        used to spend a stronger model only where it matters (e.g. song identification).
        """
        return self._complete(system, user, temperature, json_object=True, model=model)

    def complete_text(self, system: str, user: str, temperature: float = 0.3) -> str:
        """Send a chat completion expecting free-form text (e.g. a HyDE passage)."""
        return self._complete(system, user, temperature, json_object=False)

    def _complete(
        self, system: str, user: str, temperature: float, json_object: bool,
        model: str | None = None,
    ) -> str:
        if not self._providers:
            raise LLMError("No LLM provider configured (set OPENAI_API_KEY or OPENROUTER_API_KEY)")

        last_error: Exception | None = None
        for provider in self._providers:
            try:
                return self._call(provider, system, user, temperature, json_object, model)
            except LLMError as exc:
                last_error = exc
                log.warning("llm.provider_failed", provider=provider.name, error=str(exc))
        raise LLMError(f"All LLM providers failed: {last_error}")

    @staticmethod
    def _call(
        provider: _Provider,
        system: str,
        user: str,
        temperature: float,
        json_object: bool,
        model: str | None = None,
    ) -> str:
        # A per-call override only applies to OpenAI (the override ids are OpenAI
        # models); a fallback provider keeps its own model so failover still works.
        effective_model = model if (model and provider.name == "openai") else provider.model
        payload = {
            "model": effective_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        if json_object:
            payload["response_format"] = {"type": "json_object"}
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "HTTP-Referer": "https://github.com/Khayal07/MemoryLens",
            "X-Title": "MemoryLens",
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    f"{provider.base_url}/chat/completions", json=payload, headers=headers
                )
                resp.raise_for_status()
                data = resp.json()
            log.info("llm.completed", provider=provider.name, model=effective_model)
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as exc:
            raise LLMError(f"{provider.name} request failed: {exc}") from exc
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected {provider.name} response shape: {exc}") from exc
