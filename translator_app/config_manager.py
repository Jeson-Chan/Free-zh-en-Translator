"""Configuration loading and saving utilities."""

from __future__ import annotations

import json
from pathlib import Path

from translator_app.constants import CONFIG_FILE_NAME
from translator_app.exceptions import ConfigurationError
from translator_app.models import AppConfig


class ConfigManager:
    """Manage persistent application configuration."""

    def __init__(self, root_path: Path) -> None:
        """Store the project root used for configuration files."""
        self._config_path = root_path / CONFIG_FILE_NAME

    @property
    def config_path(self) -> Path:
        """Expose the absolute config file path."""
        return self._config_path

    def config_exists(self) -> bool:
        """Return whether the config file currently exists."""
        return self._config_path.exists()

    def load_config(self) -> AppConfig:
        """Load app configuration from disk or return defaults."""
        if not self._config_path.exists():
            return AppConfig()

        try:
            payload = json.loads(self._config_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise ConfigurationError(
                f"Invalid JSON in config file: {self._config_path}"
            ) from exc
        except OSError as exc:
            raise ConfigurationError(
                f"Could not read config file: {self._config_path}"
            ) from exc

        if not isinstance(payload, dict):
            raise ConfigurationError("Config file must contain a JSON object.")

        return AppConfig.from_dict(payload)

    def save_config(self, config: AppConfig) -> None:
        """Persist app configuration to disk."""
        try:
            self._config_path.write_text(
                json.dumps(config.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError as exc:
            raise ConfigurationError(
                f"Could not write config file: {self._config_path}"
            ) from exc
