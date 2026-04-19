"""Settings dialog for editing API and hotkey configuration."""

from __future__ import annotations

from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from translator_app.models import AppConfig


class SettingsDialog(QDialog):
    """Collect configuration values from the user."""

    def __init__(self, config: AppConfig, parent: QDialog | None = None) -> None:
        """Build the form using the current config values."""
        super().__init__(parent)
        self.setWindowTitle("Translator Settings")
        self.setModal(True)
        self.setMinimumWidth(420)

        self._api_key_input = QLineEdit(config.api_key)
        self._api_key_input.setEchoMode(QLineEdit.Password)

        self._api_url_input = QLineEdit(config.api_url)
        self._model_input = QLineEdit(config.model)
        self._hotkey_input = QLineEdit(config.hotkey)

        self._timeout_input = QSpinBox()
        self._timeout_input.setRange(5, 180)
        self._timeout_input.setValue(config.timeout_seconds)

        self._temperature_input = QDoubleSpinBox()
        self._temperature_input.setRange(0.0, 2.0)
        self._temperature_input.setDecimals(2)
        self._temperature_input.setSingleStep(0.1)
        self._temperature_input.setValue(config.temperature)

        form_layout = QFormLayout()
        form_layout.addRow("API Key", self._api_key_input)
        form_layout.addRow("API URL", self._api_url_input)
        form_layout.addRow("Model", self._model_input)
        form_layout.addRow("Hotkey", self._hotkey_input)
        form_layout.addRow("Timeout (s)", self._timeout_input)
        form_layout.addRow("Temperature", self._temperature_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._validate_before_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def build_config(self) -> AppConfig:
        """Return a config object from the form inputs."""
        return AppConfig(
            api_key=self._api_key_input.text().strip(),
            api_url=self._api_url_input.text().strip(),
            model=self._model_input.text().strip(),
            hotkey=self._hotkey_input.text().strip(),
            timeout_seconds=self._timeout_input.value(),
            temperature=self._temperature_input.value(),
        )

    def _validate_before_accept(self) -> None:
        """Validate required fields before closing the dialog."""
        if not self._api_key_input.text().strip():
            QMessageBox.warning(self, "Missing API Key", "DeepSeek API key is required.")
            return

        if not self._model_input.text().strip():
            QMessageBox.warning(self, "Missing Model", "Model name is required.")
            return

        if not self._api_url_input.text().strip():
            QMessageBox.warning(self, "Missing API URL", "API URL is required.")
            return

        if not self._hotkey_input.text().strip():
            QMessageBox.warning(self, "Missing Hotkey", "Hotkey is required.")
            return

        self.accept()

