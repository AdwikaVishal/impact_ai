"""
llm_client.py – Unified LLM caller.

Priority:
  1. OpenAI (if OPENAI_API_KEY is set)
  2. Ollama local (if OLLAMA_BASE_URL is reachable)
  3. Mock fallback (returns a clearly-labelled placeholder so the app never crashes)

Usage:
    from app.intelligence.llm_client import get_llm
    llm = get_llm()
    text = await llm.generate("Your prompt here")
"""

import asyncio
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# ── Lazy singleton ────────────────────────────────────────────────────────────
_llm_instance: Optional["LLMClient"] = None


def get_llm() -> "LLMClient":
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMClient()
    return _llm_instance


class LLMClient:
    """
    Wraps OpenAI, Ollama, or a mock backend behind a single async interface.
    """

    def __init__(self) -> None:
        self.openai_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.ollama_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

        if self.openai_key:
            self._backend = "openai"
            logger.info("[LLM] Using OpenAI backend (model=%s)", self.model)
        elif self._ollama_available():
            self._backend = "ollama"
            logger.info("[LLM] Using Ollama backend (model=%s)", self.model)
        else:
            self._backend = "mock"
            logger.warning(
                "[LLM] No LLM configured – using mock responses. "
                "Set OPENAI_API_KEY or start Ollama to enable real generation."
            )

    # ── Public interface ──────────────────────────────────────────────────────

    async def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Send *prompt* to the configured backend and return the response string.
        Never raises – returns an error string on failure.
        """
        try:
            if self._backend == "openai":
                return await self._openai(prompt, max_tokens)
            if self._backend == "ollama":
                return await self._ollama(prompt, max_tokens)
            return self._mock(prompt)
        except Exception as exc:  # noqa: BLE001
            logger.error("[LLM] generate() failed: %s", exc)
            return f"[LLM error: {exc}]"

    @property
    def backend(self) -> str:
        return self._backend

    # ── OpenAI ────────────────────────────────────────────────────────────────

    async def _openai(self, prompt: str, max_tokens: int) -> str:
        from openai import AsyncOpenAI  # lazy import

        client = AsyncOpenAI(api_key=self.openai_key)
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    # ── Ollama ────────────────────────────────────────────────────────────────

    async def _ollama(self, prompt: str, max_tokens: int) -> str:
        import aiohttp  # already in requirements

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as resp:
                data = await resp.json()
                return data.get("response", "").strip()

    # ── Mock ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _mock(prompt: str) -> str:
        """
        Return a clearly-labelled placeholder so the rest of the pipeline
        keeps working even without an LLM configured.
        """
        # Detect intent from prompt keywords and return a typed placeholder
        p = prompt.lower()
        if "overview" in p or "about" in p:
            return "[LLM not configured] Company overview unavailable – set OPENAI_API_KEY or start Ollama."
        if "watchout" in p or "strategic" in p or "risk" in p:
            return "- [LLM not configured] Set OPENAI_API_KEY or start Ollama to generate watchouts."
        if "market position" in p or "news" in p:
            return "[LLM not configured] Market position analysis unavailable."
        if "competitor" in p or "gap" in p:
            return '[{"name": "N/A", "strength": "LLM not configured", "gap": "Set OPENAI_API_KEY"}]'
        if "watchout" in p or "risk" in p or "strategic" in p:
            return "- LLM not configured. Set OPENAI_API_KEY or start Ollama to generate watchouts."
        if "linkedin" in p:
            return "[LLM not configured] LinkedIn message unavailable."
        if "email" in p:
            return "Subject: [LLM not configured]\nBody: Set OPENAI_API_KEY to generate email drafts."
        return "[LLM not configured] Set OPENAI_API_KEY or start Ollama."

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _ollama_available(self) -> bool:
        """Quick synchronous check – just tries to connect to Ollama's health endpoint."""
        import urllib.request

        try:
            urllib.request.urlopen(f"{self.ollama_url}/api/tags", timeout=2)
            return True
        except Exception:
            return False
