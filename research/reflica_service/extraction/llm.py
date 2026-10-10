"""Provider-neutral language-model interface.

Extraction depends only on `LLMClient`. Real providers are added as separate
adapters later; none is configured in this module and nothing here performs
network calls. `ScriptedLLM` replays fixed responses for offline tests and
demos, so every test runs without a model.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class LLMRequest:
    system: str
    user: str
    json_schema: dict[str, Any]   # the output schema the model must follow
    temperature: float = 0.0
    seed: int | None = 20261010
    max_output_tokens: int = 8192

    def sha256(self) -> str:
        blob = json.dumps({"system": self.system, "user": self.user, "schema": self.json_schema,
                           "temperature": self.temperature, "seed": self.seed,
                           "max_output_tokens": self.max_output_tokens}, sort_keys=True)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LLMResponse:
    text: str
    provider: str
    model: str
    finish_reason: str = "stop"   # "length" means the output was cut off
    usage: dict[str, int] = field(default_factory=dict)


class LLMError(RuntimeError):
    """The model could not be reached or refused the request."""


class LLMClient(Protocol):
    provider: str
    model: str

    def complete(self, request: LLMRequest) -> LLMResponse: ...


class ScriptedLLM:
    """Returns pre-written responses in order (offline tests, demos). Records requests."""

    provider = "scripted"

    def __init__(self, *responses: str | LLMResponse | Exception, model: str = "scripted-v1"):
        self.model = model
        self._responses = list(responses)
        self.requests: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        if not self._responses:
            raise LLMError("scripted LLM has no response left")
        r = self._responses.pop(0)
        if isinstance(r, Exception):
            raise r
        if isinstance(r, LLMResponse):
            return r
        return LLMResponse(text=r, provider=self.provider, model=self.model)
