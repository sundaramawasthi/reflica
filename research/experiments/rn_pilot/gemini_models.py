"""List Gemini models usable by the key in GEMINI_API_KEY (read by the SDK
from the environment; never printed). Optional --probe sends ONE tiny,
non-experimental request per named model to confirm Free-tier access.

    python gemini_models.py                     # list text-generation models
    python gemini_models.py --probe gemini-2.5-pro gemini-3.8-flash
"""
import os
import sys

from google import genai
from google.genai import types

if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit("GEMINI_API_KEY is not set in the environment.")
client = genai.Client()

if "--probe" in sys.argv:
    for mid in sys.argv[sys.argv.index("--probe") + 1:]:
        try:
            r = client.models.generate_content(
                model=mid, contents="Reply with the single word OK.",
                config=types.GenerateContentConfig(temperature=0, max_output_tokens=64))
            print(f"{mid}: usable (model_version={getattr(r, 'model_version', None)})")
        except Exception as e:  # error text never includes the key
            print(f"{mid}: NOT usable — {type(e).__name__}: {str(e)[:160]}")
else:
    for m in client.models.list():
        if "generateContent" in (m.supported_actions or []):
            print(f"{m.name}\tin={m.input_token_limit}\tout={m.output_token_limit}")
