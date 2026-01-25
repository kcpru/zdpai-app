from cachetools import TTLCache
import httpx

from app.core.config import get_settings


class MotivationMessagesProvider:
    _fallbacks = [
        "Well done, job done.",
        "Great, another task checked off.",
        "Great! Small victories make all the difference.",
    ]

    def __init__(self) -> None:
        self._cache = TTLCache(maxsize=1024, ttl=5)
        settings = get_settings()
        self._client = httpx.AsyncClient(
            base_url=settings.groq_base_url,
            headers={
                "Authorization": f"Bearer {settings.groq_api_key}"} if settings.groq_api_key else {},
        )

    async def generate_async(self, user_id: str, task_title: str | None) -> str:
        cache_key = f"motivate:{user_id}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        payload = {
            "model": "llama-3.1-8b-instant",
            "temperature": 0.8,
            "max_tokens": 60,
            "messages": [
                {
                    "role": "system",
                    "content": "Generate a short, motivating eulogy in English. Simply 1 sentence, up to 20 words. No moralizing.",
                },
                {
                    "role": "user",
                    "content": (
                        f"User completed the task: \"{task_title}\". Write a praise that relates to this completed task."
                        if task_title
                        else "User completed the task. Write a compliment."
                    ),
                },
            ],
        }

        try:
            resp = await self._client.post("chat/completions", json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            text = data.get("choices", [{}])[0].get(
                "message", {}).get("content", "").strip()
            if not text:
                text = self._fallbacks[0]
            self._cache[cache_key] = text
            return text
        except Exception:
            return self._fallbacks[0]
