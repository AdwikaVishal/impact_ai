"""
llm_client.py – LLM client with Groq as primary backend.

Priority:
  1. Groq  (set GROQ_API_KEY in .env  – fast, free tier available)
  2. OpenAI (set OPENAI_API_KEY in .env – fallback)
  3. Mock   (always available – returns labelled placeholders so the app never crashes)
"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_llm_instance = None


def get_llm() -> "LLMClient":
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMClient()
    return _llm_instance


class LLMClient:
    def __init__(self) -> None:
        self._groq_key   = os.getenv("GROQ_API_KEY")
        self._openai_key = os.getenv("OPENAI_API_KEY")
        self.model       = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self._groq_client = None

        if self._groq_key:
            try:
                from groq import Groq  # lazy import
                self._groq_client = Groq(api_key=self._groq_key)
                self._backend = "groq"
                logger.info("✅ Groq initialised (model=%s)", self.model)
            except ImportError:
                logger.warning("groq package not installed – run: pip install groq")
                self._backend = self._openai_fallback_or_mock()
            except Exception as exc:
                logger.warning("Groq init error: %s", exc)
                self._backend = self._openai_fallback_or_mock()
        else:
            logger.warning("GROQ_API_KEY not set – checking OpenAI fallback")
            self._backend = self._openai_fallback_or_mock()

    def _openai_fallback_or_mock(self) -> str:
        if self._openai_key:
            logger.info("Using OpenAI as fallback backend")
            return "openai"
        logger.warning("No LLM configured – using mock responses")
        return "mock"

    @property
    def backend(self) -> str:
        return self._backend

    async def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text. Never raises – returns an error string on failure."""
        try:
            if self._backend == "groq":
                return await self._groq(prompt, max_tokens)
            if self._backend == "openai":
                return await self._openai(prompt, max_tokens)
            return self._mock(prompt)
        except Exception as exc:  # noqa: BLE001
            logger.error("LLM generate() failed: %s", exc)
            return f"[LLM error: {str(exc)[:120]}]"

    # ── Groq ──────────────────────────────────────────────────────────────────

    async def _groq(self, prompt: str, max_tokens: int) -> str:
        import asyncio

        def _sync() -> str:
            response = self._groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional market research analyst. "
                            "Provide concise, factual, actionable insights."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync)

    # ── OpenAI ────────────────────────────────────────────────────────────────

    async def _openai(self, prompt: str, max_tokens: int) -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self._openai_key)
        response = await client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    # ── Mock ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _mock(prompt: str) -> str:
        p = prompt.lower()
        if "overview" in p or "about" in p:
            return "[Mock] Company overview – set GROQ_API_KEY for real output."
        if "watchout" in p or "risk" in p:
            return '["Set GROQ_API_KEY to generate real watchouts"]'
        if "market position" in p or "news" in p:
            return "[Mock] Market position – set GROQ_API_KEY for real output."
        if "competitor" in p or "gap" in p:
            return '[{"name": "Competitor", "strength": "Mock", "gap": "Set GROQ_API_KEY"}]'
        if "linkedin" in p:
            return "[Mock] LinkedIn message – set GROQ_API_KEY for real output."
        if "email" in p:
            return "Subject: [Mock]\nBody: Set GROQ_API_KEY to generate real emails."
        return "[Mock] Set GROQ_API_KEY in .env to enable real LLM responses."
