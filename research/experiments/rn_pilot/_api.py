"""Minimal OpenAI HTTP client (stdlib only). The key is read from the
environment at call time and never logged, returned or written anywhere."""
import json
import os
import urllib.error
import urllib.request

# Provider is chosen by environment; both speak the OpenAI-compatible API.
PROVIDERS = {
    "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY"),
    "nvidia": ("https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY"),
}
PROVIDER = os.environ.get("REFLICA_LLM_PROVIDER", "openai")
BASE, KEY_ENV = PROVIDERS[PROVIDER]


def _req(method: str, path: str, body: dict | None = None) -> dict:
    key = os.environ.get(KEY_ENV)
    if not key:
        raise SystemExit(f"{KEY_ENV} is not set in the environment.")
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=int(os.environ.get("REFLICA_HTTP_TIMEOUT", "600"))) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:  # body never contains the key
        raise SystemExit(f"HTTP {e.code}: {e.read().decode()[:500]}") from None


def list_models() -> list[str]:
    return sorted(m["id"] for m in _req("GET", "/models")["data"])


def chat(model: str, system: str, user: str, temperature: float, seed: int, max_tokens: int,
         extra: dict | None = None) -> dict:
    tok = "max_tokens" if PROVIDER == "nvidia" else "max_completion_tokens"
    body = {
        "model": model, "temperature": temperature, "seed": seed, tok: max_tokens, "stream": False,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }
    body.update(extra or {})
    return _req("POST", "/chat/completions", body)
