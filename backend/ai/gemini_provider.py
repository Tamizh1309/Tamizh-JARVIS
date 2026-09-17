import logging
from typing import Optional
import httpx

from ai.provider import AIProvider

logger = logging.getLogger("tamizh_jarvis.ai.gemini")


class GeminiProvider(AIProvider):
    """Google Gemini AI Provider using async REST interface with hardening."""

    def __init__(self, api_key: Optional[str], model: str = "gemini-2.5-flash", timeout_seconds: float = 15.0):
        self.api_key = api_key.strip() if api_key else None
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @property
    def name(self) -> str:
        return "gemini"

    def _masked_key(self) -> str:
        if not self.api_key:
            return "NONE"
        if len(self.api_key) <= 8:
            return "***"
        return f"{self.api_key[:4]}...{self.api_key[-4:]}"

    async def is_available(self) -> bool:
        if not self.api_key or len(self.api_key) < 10:
            return False
        # Prevent false keys
        if self.api_key.startswith("AQ."):
            # Google Cloud OAuth token, not Gemini Studio key
            return False
        return True

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        if not await self.is_available():
            raise RuntimeError(f"Gemini API key is invalid or not configured (key: {self._masked_key()}).")

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

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            try:
                response = await client.post(url, json=payload)
                
                # Check for rate limit specifically
                if response.status_code == 429:
                    logger.warning("Gemini rate limit exceeded (HTTP 429).")
                    raise RuntimeError("Gemini API rate limit exceeded. Please wait a moment or switch to local provider.")

                response.raise_for_status()
                data = response.json()

                # Robust parsing for candidates
                candidates = data.get("candidates", [])
                if not candidates:
                    logger.warning("Gemini returned empty candidates: %s", data)
                    return ""

                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"]

                return ""

            except httpx.TimeoutException as e:
                logger.error("Gemini API call timed out after %.1f seconds", self.timeout_seconds)
                raise RuntimeError(f"Gemini generation timed out after {self.timeout_seconds}s") from e

            except httpx.HTTPStatusError as e:
                # Never expose the API key in the logged URL or error message
                clean_err = e.response.text.replace(self.api_key, self._masked_key()) if self.api_key else e.response.text
                logger.error("Gemini HTTP Error %s: %s", e.response.status_code, clean_err)
                raise RuntimeError(f"Gemini API error (Status {e.response.status_code}): {clean_err}") from e

            except Exception as e:
                logger.error("Gemini unexpected error: %s", str(e))
                raise RuntimeError(f"Gemini generation error: {str(e)}") from e
