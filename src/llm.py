"""OpenAI LLM client helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    requests: int = 0

    def __sub__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            prompt_tokens=self.prompt_tokens - other.prompt_tokens,
            completion_tokens=self.completion_tokens - other.completion_tokens,
            total_tokens=self.total_tokens - other.total_tokens,
            requests=self.requests - other.requests,
        )


class OpenAIJSONClient:
    """Small wrapper around OpenAI chat completions for JSON outputs."""

    def __init__(self, api_key: str, model: str) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The openai package is not installed. Run `pip install -e .` first."
            ) from exc

        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._usage = TokenUsage()

    @property
    def usage(self) -> TokenUsage:
        return self._usage

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float | None = None,
        response_schema: dict[str, Any] | None = None,
        schema_name: str = "llm_response",
    ) -> dict[str, Any]:
        response_format: dict[str, Any]
        if response_schema is None:
            response_format = {"type": "json_object"}
        else:
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": response_schema,
                },
            }
        request = dict(
            model=self._model,
            response_format=response_format,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        if temperature is not None:
            request["temperature"] = temperature

        try:
            response = self._client.chat.completions.create(**request)
        except Exception as exc:
            if temperature is None or not _is_unsupported_temperature_error(exc):
                raise
            request.pop("temperature", None)
            response = self._client.chat.completions.create(**request)

        self._record_usage(response)
        content = response.choices[0].message.content or "{}"
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Model returned invalid JSON: {content}") from exc

    def _record_usage(self, response: Any) -> None:
        usage = getattr(response, "usage", None)
        self._usage = TokenUsage(
            prompt_tokens=self._usage.prompt_tokens
            + int(getattr(usage, "prompt_tokens", 0) or 0),
            completion_tokens=self._usage.completion_tokens
            + int(getattr(usage, "completion_tokens", 0) or 0),
            total_tokens=self._usage.total_tokens
            + int(getattr(usage, "total_tokens", 0) or 0),
            requests=self._usage.requests + 1,
        )


def _is_unsupported_temperature_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "temperature" in message and "unsupported" in message
