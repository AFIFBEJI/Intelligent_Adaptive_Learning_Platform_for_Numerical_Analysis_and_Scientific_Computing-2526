"""
Diagnose the AI model picker.

The tutor's model picker button only appears when AT LEAST TWO providers
load successfully at startup (Ollama local + OpenAI cloud). This script
tells you exactly which providers load and why the other one fails.

Run it from the backend folder, inside your venv:

    cd backend
    python scripts/diagnose_llm.py
"""
import sys
from pathlib import Path

# Allow importing the app package when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main() -> None:
    print("=" * 60)
    print(" LLM PICKER DIAGNOSIS")
    print("=" * 60)

    # 1. Settings ----------------------------------------------------
    from app.core.config import get_settings

    s = get_settings()
    key = (s.OPENAI_API_KEY or "").strip()
    print("\n[1] Settings read from .env")
    print(f"    LLM_PROVIDER        = {s.LLM_PROVIDER}")
    print(f"    LLM_PICKER_ENABLED  = {s.LLM_PICKER_ENABLED}")
    print(f"    LLM_MODEL_NAME      = {s.LLM_MODEL_NAME}")
    print(f"    OLLAMA_MODEL        = {s.OLLAMA_MODEL}")
    print(f"    OLLAMA_BASE_URL     = {s.OLLAMA_BASE_URL}")
    if key:
        print(f"    OPENAI_API_KEY      = present ({len(key)} chars, starts '{key[:7]}...')")
    else:
        print("    OPENAI_API_KEY      = MISSING / empty  <-- OpenAI will NOT load")

    # 2. Python dependencies ----------------------------------------
    # We import the ACTUAL classes used by the service (not just the
    # top package), because some packages import lazily and only fail
    # when the class is really pulled in (e.g. via tiktoken).
    print("\n[2] Python packages (real import of the classes used)")
    try:
        from langchain_ollama import ChatOllama  # noqa: F401
        print("    langchain_ollama.ChatOllama  = OK")
    except Exception as exc:  # noqa: BLE001
        print(f"    langchain_ollama.ChatOllama  = FAIL -> {type(exc).__name__}: {exc}")
    try:
        from langchain_openai import ChatOpenAI  # noqa: F401
        print("    langchain_openai.ChatOpenAI  = OK")
    except Exception as exc:  # noqa: BLE001
        print(f"    langchain_openai.ChatOpenAI  = FAIL -> {type(exc).__name__}: {exc}")

    # tiktoken functional check (OpenAI needs it to count tokens)
    try:
        import tiktoken
        tiktoken.get_encoding("cl100k_base")
        print(f"    tiktoken {tiktoken.__version__:12} = OK (encoding loads)")
    except Exception as exc:  # noqa: BLE001
        print(f"    tiktoken = FAIL -> {type(exc).__name__}: {exc}")

    # 3. Is the local Ollama server reachable? ----------------------
    print("\n[3] Ollama server reachability")
    try:
        import urllib.request

        url = s.OLLAMA_BASE_URL.rstrip("/") + "/api/tags"
        with urllib.request.urlopen(url, timeout=4) as resp:  # noqa: S310
            ok = resp.status == 200
        print(f"    GET {url} -> {'OK' if ok else resp.status}")
    except Exception as exc:  # noqa: BLE001
        print(f"    Ollama not reachable at {s.OLLAMA_BASE_URL} ({exc})")
        print("    (Start Ollama / Docker Desktop. The client may still load, "
              "but answers will fail.)")

    # 4. What the backend actually loaded ---------------------------
    print("\n[4] Providers actually loaded by the backend")
    from app.services.llm_service import llm_service

    providers = llm_service.available_providers()
    for pid in ("ollama", "openai"):
        status = "LOADED" if pid in providers else "not loaded"
        model = llm_service.model_name_for(pid) if pid in providers else "-"
        print(f"    {pid:8} = {status:11} (model: {model})")

    # 5. Verdict -----------------------------------------------------
    print("\n[5] Verdict")
    n = len(providers)
    if n >= 2 and s.LLM_PICKER_ENABLED:
        print("    OK -> the picker button SHOULD appear on the Tutor page.")
        print("    If it still does not show: hard-refresh the page (Ctrl+Shift+R)")
        print("    and make sure the frontend talks to THIS backend.")
    elif n >= 2 and not s.LLM_PICKER_ENABLED:
        print("    Two providers loaded but LLM_PICKER_ENABLED is false.")
        print("    -> set LLM_PICKER_ENABLED=true in .env and restart.")
    else:
        print(f"    Only {n} provider loaded -> the button stays hidden.")
        print("    Fix the provider marked 'not loaded' above (key, package, or Ollama),")
        print("    then RESTART the backend (uvicorn) so it reloads the providers.")
    print("=" * 60)


if __name__ == "__main__":
    main()
