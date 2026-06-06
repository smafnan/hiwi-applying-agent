"""
NVIDIA NIM LLM shim.

The original plan was written against the Anthropic SDK (`anthropic.Anthropic()` +
`client.messages.create(...)` returning `resp.content[0].text`). This module provides
a drop-in replacement with the SAME surface so each agent only changes one import line:

    import anthropic            ->   from agents import llm as anthropic

`anthropic.Anthropic()` then resolves to the shim below, which routes to NVIDIA NIM's
OpenAI-compatible endpoint. Any Claude `model=` argument passed by the legacy code is
ignored and remapped to NVIDIA_MODEL — the real model is centralized here.

Why not the safety-guard model originally supplied: it is a content classifier and
returns safety labels, not generated text/JSON. We use an instruction model instead.
"""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
BASE_URL = os.environ.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
# Verified accessible on this account (meta/llama-3.3-70b-instruct returns clean JSON).
DEFAULT_MODEL = os.environ.get("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")

_MAX_RETRIES = 4


class _TextBlock:
    def __init__(self, text: str):
        self.text = text


class _Response:
    """Mimics anthropic response: resp.content[0].text"""
    def __init__(self, text: str):
        self.content = [_TextBlock(text)]


class _Messages:
    def create(self, model=None, max_tokens=512, system=None,
               messages=None, temperature=0.2, **kwargs):
        chat_messages = []
        if system:
            chat_messages.append({"role": "system", "content": system})
        chat_messages.extend(messages or [])

        payload = {
            "model": DEFAULT_MODEL,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json",
        }

        last_err = None
        for attempt in range(_MAX_RETRIES):
            try:
                r = requests.post(
                    f"{BASE_URL}/chat/completions",
                    headers=headers, json=payload, timeout=120,
                )
                if r.status_code == 429:  # rate limited — back off
                    wait = 2 ** attempt
                    time.sleep(wait)
                    last_err = f"429 rate limit (attempt {attempt + 1})"
                    continue
                r.raise_for_status()
                content = r.json()["choices"][0]["message"]["content"]
                return _Response(content)
            except requests.HTTPError as e:
                last_err = f"HTTP {r.status_code}: {r.text[:200]}"
                if 400 <= r.status_code < 500 and r.status_code != 429:
                    break  # client error — don't retry
                time.sleep(2 ** attempt)
            except Exception as e:
                last_err = f"{type(e).__name__}: {e}"
                time.sleep(2 ** attempt)

        raise RuntimeError(f"NVIDIA NIM call failed after {_MAX_RETRIES} attempts: {last_err}")


class Anthropic:
    """Drop-in stand-in for anthropic.Anthropic()."""
    def __init__(self, *args, **kwargs):
        self.messages = _Messages()
