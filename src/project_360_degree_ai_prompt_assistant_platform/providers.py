"""Optional live provider integrations using plain HTTP."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from project_360_degree_ai_prompt_assistant_platform.settings import AppSettings


class ProviderError(RuntimeError):
    """Raised when a live model call cannot be completed."""


def generate_with_provider(
    *,
    provider: str,
    prompt: str,
    model: str | None,
    settings: AppSettings,
) -> str:
    if provider == "local":
        return ""
    if provider == "openai":
        return _call_openai(prompt=prompt, model=model or settings.openai_model)
    if provider == "gemini":
        return _call_gemini(prompt=prompt, model=model or settings.gemini_model)
    raise ProviderError(f"Unsupported provider: {provider}")


def _call_openai(*, prompt: str, model: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ProviderError("OPENAI_API_KEY is not set.")

    payload = {
        "model": model,
        "input": [
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Rewrite the user's prompt into a sharper final prompt. Preserve intent and be concise.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            },
        ],
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    return _read_openai_response(request)


def _read_openai_response(request: urllib.request.Request) -> str:
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:  # pragma: no cover - network dependent
        message = exc.read().decode("utf-8", errors="replace")
        raise ProviderError(f"OpenAI request failed: {message}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network dependent
        raise ProviderError(f"OpenAI connection failed: {exc.reason}") from exc

    if isinstance(payload.get("output_text"), str) and payload["output_text"].strip():
        return payload["output_text"].strip()

    for item in payload.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                return str(text).strip()

    raise ProviderError("OpenAI returned no text output.")


def _call_gemini(*, prompt: str, model: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ProviderError("GEMINI_API_KEY is not set.")

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Rewrite the following into a stronger final prompt while preserving intent.\n\n"
                            f"{prompt}"
                        )
                    }
                ],
            }
        ]
    }
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    return _read_gemini_response(request)


def _read_gemini_response(request: urllib.request.Request) -> str:
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:  # pragma: no cover - network dependent
        message = exc.read().decode("utf-8", errors="replace")
        raise ProviderError(f"Gemini request failed: {message}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network dependent
        raise ProviderError(f"Gemini connection failed: {exc.reason}") from exc

    for candidate in payload.get("candidates", []):
        parts = candidate.get("content", {}).get("parts", [])
        text = "\n".join(part.get("text", "").strip() for part in parts if part.get("text"))
        if text.strip():
            return text.strip()

    raise ProviderError("Gemini returned no text output.")
