"""Floating translator window implementation."""

from __future__ import annotations

import logging
from typing import Optional

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QCloseEvent, QMouseEvent
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QStyle,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from translator_app.config_manager import ConfigManager
from translator_app.exceptions import ConfigurationError, HistoryError, HotkeyError
from translator_app.history_manager import HistoryManager
from translator_app.hotkey_manager import GlobalHotkeyManager
from translator_app.language import describe_language
from translator_app.models import AppConfig, HistoryEntry, TranslationResult
from translator_app.settings_dialog import SettingsDialog
from translator_app.translation_service import TranslationService
from translator_app.worker import TranslationWorker

LOGGER = logging.getLogger(__name__)


class DraggableHeaderFrame(QFrame):
    """Simple draggable header for the frameless floating window."""

    def __init__(self, parent_window: QWidget) -> None:
        """Store the parent window that should move during drag."""
        super().__init__(parent_window)
        self._parent_window = parent_window
        self._drag_offset: Optional[QPoint] = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Start dragging when the left mouse button is pressed."""
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPos() - self._parent_window.frameGeometry().topLeft()
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Move the parent window while dragging."""
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self._parent_window.move(event.globalPos() - self._drag_offset)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Stop dragging once the mouse button is released."""
        self._drag_offset = None
        super().mouseReleaseEvent(event)


class ClickToCopyTextEdit(QTextEdit):
    """Read-only result box that copies its contents on click."""

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Copy the current result to the clipboard when clicked."""
        if self.toPlainText().strip():
            QApplication.clipboard().setText(self.toPlainText())

        super().mousePressEvent(event)


class HistoryDialog(QDialog):
    """Display the recent translation history."""

    def __init__(self, history_text: str, parent: QWidget | None = None) -> None:
        """Render the formatted history text."""
        super().__init__(parent)
        self.setWindowTitle("Recent History")
        self.resize(540, 420)

        viewer = QTextEdit()
        viewer.setReadOnly(True)
        viewer.setPlainText(history_text)

        layout = QVBoxLayout()
        layout.addWidget(viewer)
        self.setLayout(layout)


class FloatingTranslatorWindow(QWidget):
    """Main floating translator UI."""

    def __init__(
        self,
        service: TranslationService,
        config_manager: ConfigManager,
        history_manager: HistoryManager,
    ) -> None:
        """Create the floating window and supporting helpers."""
        super().__init__()
        self._service = service
        self._config_manager = config_manager
        self._history_manager = history_manager
        self._worker: Optional[TranslationWorker] = None
        self._tray_icon: Optional[QSystemTrayIcon] = None
        self._hotkey_manager: Optional[GlobalHotkeyManager] = None

        self._input_box = QTextEdit()
        self._result_box = ClickToCopyTextEdit()
        self._translate_button = QPushButton("Translate")
        self._status_label = QLabel("Ready")

        self._configure_window()
        self._build_ui()
        self._create_tray_icon()
        self._position_bottom_right()
        self._register_hotkey(self._config_manager.load_config())

    def _configure_window(self) -> None:
        """Apply floating tool window settings."""
        self.setWindowTitle("Academic Translator")
        self.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.resize(460, 520)
        self.setMinimumSize(420, 360)

    def _build_ui(self) -> None:
        """Build the floating window layout."""
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(8)

        header = DraggableHeaderFrame(self)
        header.setFrameShape(QFrame.StyledPanel)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 6, 8, 6)

        title_label = QLabel("Academic Translator")
        title_label.setStyleSheet("font-weight: bold;")

        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self._show_settings)

        history_button = QPushButton("History")
        history_button.clicked.connect(self._show_history)

        paste_button = QPushButton("Paste")
        paste_button.clicked.connect(self._paste_clipboard)

        hide_button = QPushButton("Hide")
        hide_button.clicked.connect(self.toggle_visibility)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(history_button)
        header_layout.addWidget(settings_button)
        header_layout.addWidget(paste_button)
        header_layout.addWidget(hide_button)
        header.setLayout(header_layout)

        self._input_box.setPlaceholderText("Paste English or Chinese text here...")
        self._result_box.setPlaceholderText("Translation result appears here. Click to copy.")
        self._result_box.setReadOnly(True)

        self._translate_button.clicked.connect(self._start_translation)

        root_layout.addWidget(header)
        root_layout.addWidget(QLabel("Source Text"))
        root_layout.addWidget(self._input_box)
        root_layout.addWidget(self._translate_button)
        root_layout.addWidget(QLabel("Translated Text"))
        root_layout.addWidget(self._result_box)
        root_layout.addWidget(self._status_label)
        self.setLayout(root_layout)

    def _create_tray_icon(self) -> None:
        """Create the system tray icon and its actions."""
        tray_icon = QSystemTrayIcon(self.style().standardIcon(QStyle.SP_ComputerIcon), self)
        menu = QMenu(self)

        toggle_action = QAction("Show / Hide", self)
        toggle_action.triggered.connect(self.toggle_visibility)
        menu.addAction(toggle_action)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self._show_settings)
        menu.addAction(settings_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)

        tray_icon.setToolTip("Academic Floating Translator")
        tray_icon.setContextMenu(menu)
        tray_icon.activated.connect(self._handle_tray_activation)
        tray_icon.show()

        self._tray_icon = tray_icon

    def _handle_tray_activation(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Toggle the window when the tray icon is clicked."""
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_visibility()

    def _position_bottom_right(self) -> None:
        """Place the floating window near the bottom-right corner."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return

        available_geometry = screen.availableGeometry()
        x_position = available_geometry.right() - self.width() - 20
        y_position = available_geometry.bottom() - self.height() - 20
        self.move(x_position, y_position)

    def _register_hotkey(self, config: AppConfig) -> None:
        """Register the configured global hotkey."""
        self._stop_hotkey()
        self._hotkey_manager = GlobalHotkeyManager(config.hotkey)
        self._hotkey_manager.activated.connect(self.toggle_visibility)

        try:
            self._hotkey_manager.start()
        except HotkeyError as exc:
            LOGGER.warning("Global hotkey failed to start: %s", exc)
            self._update_status(str(exc))
            QMessageBox.warning(
                self,
                "Hotkey Warning",
                f"{exc}\nThe tray icon still lets you show or hide the window.",
            )

    def _stop_hotkey(self) -> None:
        """Stop the current global hotkey listener if one exists."""
        if self._hotkey_manager is not None:
            self._hotkey_manager.stop()
            self._hotkey_manager = None

    def _paste_clipboard(self) -> None:
        """Paste plain text from the system clipboard into the input area."""
        clipboard_text = QApplication.clipboard().text().strip()
        if not clipboard_text:
            QMessageBox.information(self, "Clipboard Empty", "No text found in the clipboard.")
            return

        self._input_box.setPlainText(clipboard_text)
        self._update_status("Clipboard content pasted.")

    def _start_translation(self) -> None:
        """Start a background translation job for the current input."""
        text = self._input_box.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "No Text", "Please enter or paste text first.")
            return

        if self._worker is not None and self._worker.isRunning():
            QMessageBox.information(
                self,
                "Translation Running",
                "Please wait for the current translation to finish.",
            )
            return

        self._translate_button.setEnabled(False)
        self._update_status("Translating...")
        self._worker = TranslationWorker(self._service, text)
        self._worker.succeeded.connect(self._handle_translation_success)
        self._worker.failed.connect(self._handle_translation_failure)
        self._worker.finished.connect(self._finish_translation)
        self._worker.start()

    def _handle_translation_success(self, result: TranslationResult) -> None:
        """Update the UI with a completed translation."""
        self._result_box.setPlainText(result.translated_text)
        QApplication.clipboard().setText(result.translated_text)
        source_label = describe_language(result.source_language)
        target_label = describe_language(result.target_language)
        self._update_status(
            f"Translated {source_label} -> {target_label} with {result.model}. Result copied."
        )

    def _handle_translation_failure(self, error_message: str) -> None:
        """Show a user-friendly message for translation failures."""
        self._update_status(error_message)
        QMessageBox.warning(self, "Translation Failed", error_message)

    def _finish_translation(self) -> None:
        """Reset UI state after the worker finishes."""
        self._translate_button.setEnabled(True)

    def _show_settings(self) -> None:
        """Open the settings dialog and persist changes."""
        try:
            current_config = self._config_manager.load_config()
        except ConfigurationError as exc:
            QMessageBox.warning(self, "Config Error", str(exc))
            current_config = AppConfig()

        dialog = SettingsDialog(current_config, self)
        if dialog.exec_() != QDialog.Accepted:
            return

        try:
            new_config = dialog.build_config()
            self._config_manager.save_config(new_config)
            self._register_hotkey(new_config)
        except ConfigurationError as exc:
            QMessageBox.critical(self, "Save Failed", str(exc))
            return

        self._update_status("Settings saved.")

    def _show_history(self) -> None:
        """Display the most recent translations in a dialog."""
        try:
            entries = self._history_manager.load_entries()
        except HistoryError as exc:
            QMessageBox.warning(self, "History Error", str(exc))
            return

        if not entries:
            QMessageBox.information(self, "No History", "No translations have been saved yet.")
            return

        history_text = self._format_history(entries)
        HistoryDialog(history_text, self).exec_()

    def _format_history(self, entries: list[HistoryEntry]) -> str:
        """Format history entries for display."""
        blocks = []
        for entry in entries:
            block = (
                f"[{entry.timestamp}] {entry.source_language} -> {entry.target_language}\n"
                f"Source:\n{entry.source_text}\n\n"
                f"Translation:\n{entry.translated_text}"
            )
            blocks.append(block)

        return f"\n{('-' * 60)}\n\n".join(blocks)

    def _update_status(self, message: str) -> None:
        """Update the status label with the latest message."""
        self._status_label.setText(message)

    def toggle_visibility(self) -> None:
        """Show or hide the floating window."""
        if self.isVisible():
            self.hide()
            return

        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Clean up long-lived helpers when the application exits."""
        self._stop_hotkey()
        if self._tray_icon is not None:
            self._tray_icon.hide()

        super().closeEvent(event)
