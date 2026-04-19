"""DeepSeek API client."""

from __future__ import annotations

import logging

import requests

from translator_app.constants import SYSTEM_PROMPT
from translator_app.exceptions import DeepSeekAPIError
from translator_app.models import AppConfig

LOGGER = logging.getLogger(__name__)


class DeepSeekClient:
    """Send translation requests to a DeepSeek-compatible API."""

    def __init__(self, config: AppConfig) -> None:
        """Store request configuration for future API calls."""
        self._config = config

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        """Translate a single text block and return the model output."""
        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._config.model,
            "temperature": self._config.temperature,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": self._build_user_message(
                        text=text,
                        source_language=source_language,
                        target_language=target_language,
                    ),
                },
            ],
        }

        LOGGER.info(
            "Sending translation request with model=%s source=%s target=%s",
            self._config.model,
            source_language,
            target_language,
        )

        try:
            response = requests.post(
                self._config.api_url,
                headers=headers,
                json=payload,
                timeout=self._config.timeout_seconds,
            )
            response.raise_for_status()
            response_payload = response.json()
        except requests.HTTPError as exc:
            raise DeepSeekAPIError(
                f"DeepSeek API returned an HTTP error: {exc}"
            ) from exc
        except requests.RequestException as exc:
            raise DeepSeekAPIError(
                f"DeepSeek API request failed: {exc}"
            ) from exc
        except ValueError as exc:
            raise DeepSeekAPIError("DeepSeek API returned invalid JSON.") from exc

        content = self._extract_content(response_payload)
        if not content:
            raise DeepSeekAPIError("DeepSeek API returned an empty translation result.")

        return content

    @staticmethod
    def _build_user_message(
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        """Build the user message sent to the model."""
        return (
            f"Source language: {source_language}\n"
            f"Target language: {target_language}\n"
            "Please preserve formatting and academic terminology.\n\n"
            f"{text}"
        )

    @staticmethod
    def _extract_content(payload: dict) -> str:
        """Extract the translated message text from the API response."""
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise DeepSeekAPIError("DeepSeek API response is missing choices.")

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise DeepSeekAPIError("DeepSeek API choice format is invalid.")

        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise DeepSeekAPIError("DeepSeek API response is missing message data.")

        content = message.get("content", "")
        if not isinstance(content, str):
            raise DeepSeekAPIError("DeepSeek API message content is invalid.")

        return content.strip()

