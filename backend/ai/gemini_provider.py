import logging
from typing import Optional
import httpx

from ai.provider import AIProvider

logger = logging.getLogger("tamizh_jarvis.ai.gemini")


class GeminiProvider(AIProvider):
    """Google Gemini AI Provider using direct async REST interface."""

    def __init__(self, api_key: Optional[str], model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @property
    def name(self) -> str:
        return "gemini"

    async def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 0)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        if not await self.is_available():
            raise RuntimeError("Gemini API key is not configured or empty.")

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        generation_config = {}
        if json_mode:
            generation_config["responseMimeType"] = "application/json"

        if generation_config:
            payload["generationConfig"] = generation_config

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
                return ""
            except httpx.HTTPStatusError as e:
                logger.error("Gemini HTTP Error %s: %s", e.response.status_code, e.response.text)
                raise RuntimeError(f"Gemini API returned status {e.response.status_code}: {e.response.text}") from e
            except Exception as e:
                logger.error("Gemini generation failed: %s", str(e))
                raise RuntimeError(f"Gemini generation error: {str(e)}") from e
