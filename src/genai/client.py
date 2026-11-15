import os

import requests


def online_available():
    return bool(os.environ.get("OPENAI_API_KEY"))


def chat(system, user, model, timeout=60):
    """Call any OpenAI-compatible chat endpoint. Key and URL come from environment variables.

    OPENAI_API_KEY (required), OPENAI_BASE_URL (default https://api.openai.com/v1), OPENAI_MODEL (optional).
    Works with OpenAI, Azure OpenAI v1 endpoints, GitHub Models and local servers such as Ollama.
    """
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    resp = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        json={
            "model": os.environ.get("OPENAI_MODEL", model),
            "temperature": 0.2,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
