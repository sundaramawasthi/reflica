"""List model ids this key can use, then probe named ids with one tiny
non-experimental request and report the model the server says answered.

    REFLICA_LLM_PROVIDER=nvidia python list_models.py [--probe id ...]
"""
import sys

from _api import chat, list_models

if __name__ == "__main__":
    ids = list_models()
    if "--probe" not in sys.argv:
        print("\n".join(ids))
    for mid in sys.argv[sys.argv.index("--probe") + 1:] if "--probe" in sys.argv else []:
        listed = mid in ids
        try:
            r = chat(mid, "Reply with JSON.", 'Return {"ok": true}.', 0, 0, 256)
            served = r.get("model")
            print(f"{mid}: listed={listed} usable served={served} redirect={served != mid}", flush=True)
        except (SystemExit, TimeoutError, OSError) as e:
            print(f"{mid}: listed={listed} NOT usable — {type(e).__name__}: {str(e)[:150]}", flush=True)
