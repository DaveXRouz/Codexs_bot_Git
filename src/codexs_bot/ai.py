from __future__ import annotations

import logging
from typing import Optional

import httpx

from .localization import Language

logger = logging.getLogger(__name__)


SYSTEM_PROMPTS = {
    Language.EN: (
        "You are Codexs, a bilingual (English/Farsi) automation studio assistant. "
        "Always keep responses concise, confident, and actionable—like a Tesla/SpaceX operator. "
        "If a user asks for something the bot cannot do, guide them toward the closest supported flow "
        "(Apply, About, Updates, Contact) or suggest typing /menu. "
        "Never invent new features or promises. "
        "When replying in English, use polished yet simple HTML (bold/italic) sparingly."
    ),
    Language.FA: (
        "شما دستیار دوزبانه Codexs هستید. پاسخ‌ها باید کوتاه، دقیق و حرفه‌ای باشند. "
        "اگر کاربر چیزی خارج از توانایی‌های ربات خواست، او را به نزدیک‌ترین بخش موجود "
        "راهنمایی کنید (درخواست همکاری، درباره، به‌روزرسانی‌ها، تماس) یا بگویید /menu را تایپ کند. "
        "هیچ قابلیتی را اختراع نکنید و از لحن مینیمال استفاده کنید."
    ),
}


class OpenAIFallback:
    def __init__(
        self,
        api_key: Optional[str],
        model: str = "gpt-4o-mini",
        timeout: float = 15.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def generate_reply(
        self,
        language: Language,
        context_text: str,
        user_text: str,
    ) -> Optional[str]:
        if not self.api_key:
            return None

        system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS[Language.EN])
        user_prompt = (
            f"{context_text.strip()}\n\n"
            f"User message:\n{user_text.strip()}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 350,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # pragma: no cover - network errors
            logger.warning("OpenAI fallback request failed: %s", exc)
            return None

        choices = data.get("choices") or []
        if not choices:
            return None
        message = choices[0].get("message", {})
        content = (message.get("content") or "").strip()
        return content or None

