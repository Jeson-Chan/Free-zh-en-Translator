"""Application-wide constants."""

APP_NAME = "Academic Floating Translator"
CONFIG_FILE_NAME = "config.json"
HISTORY_FILE_NAME = "history.json"
LOG_FILE_NAME = "translator.log"

DEFAULT_API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TIMEOUT_SECONDS = 45
DEFAULT_TEMPERATURE = 0.2
DEFAULT_HOTKEY = "<ctrl>+t"
MAX_HISTORY_ITEMS = 10

SYSTEM_PROMPT = (
    "你是一位专业的学术翻译专家，请将以下英文（或中文）内容准确翻译为中文（或英文），"
    "保留专业术语的准确性，并保持原文格式。"
)

