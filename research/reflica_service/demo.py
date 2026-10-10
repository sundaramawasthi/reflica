"""Run the API locally with a SCRIPTED model (no real LLM) for demos and live tests.

    python -m reflica_service.demo --response tests/service/data/extraction/good_response.json

Every extraction returns the given hand-written response, whatever text is sent;
quotes that are not in the text are then marked as inferred by the usual checks.
`/v1/health` reports the model as "scripted/fixed-response-demo" and the app
shows that name on every proposal, so a demo is never mistaken for real
extraction. Binds to 127.0.0.1 only.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .extraction.llm import LLMRequest, LLMResponse


class FixedResponseLLM:
    provider = "scripted"
    model = "fixed-response-demo"

    def __init__(self, text: str):
        self._text = text

    def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text=self._text, provider=self.provider, model=self.model)


def main(argv: list[str] | None = None) -> None:  # pragma: no cover - manual use
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--response", required=True, type=Path,
                    help="file holding the model output to replay")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args(argv)
    import uvicorn

    from .app import create_app
    uvicorn.run(create_app(llm=FixedResponseLLM(args.response.read_text())),
                host="127.0.0.1", port=args.port)


if __name__ == "__main__":  # pragma: no cover
    main()
