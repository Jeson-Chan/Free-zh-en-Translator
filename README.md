# Academic Floating Translator

A desktop floating translation tool built with Python and PyQt5. It targets Chinese and English academic or professional text and uses the DeepSeek API through the OpenAI-compatible chat completions format.

## Features

- Floating always-on-top window with drag support
- Source input area, translate button, and result display
- DeepSeek API integration with an academic translation system prompt
- Auto language direction selection between Chinese and English
- Clipboard paste support
- Click translation result to copy it to the clipboard
- Recent history storage for the latest 10 translations
- Global hotkey support for show or hide
- First-run settings dialog for DeepSeek API configuration

## Project Structure

```text
d:\MyProject
|-- main.py
|-- README.md
|-- requirements.txt
|-- config.example.json
|-- translator_app
|   |-- __init__.py
|   |-- config_manager.py
|   |-- constants.py
|   |-- deepseek_client.py
|   |-- exceptions.py
|   |-- floating_window.py
|   |-- history_manager.py
|   |-- hotkey_manager.py
|   |-- language.py
|   |-- logging_config.py
|   |-- models.py
|   |-- settings_dialog.py
|   |-- translation_service.py
|   `-- worker.py
`-- tests
    `-- test_language.py
```

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `config.example.json` to `config.json`, or let the app prompt you on first launch.
4. Put your DeepSeek API key in `config.json`.

## Run

```bash
python main.py
```

## DeepSeek Configuration

The application sends requests to:

- `https://api.deepseek.com/chat/completions`

Default model:

- `deepseek-chat`

You can change the model in the settings dialog if you want to use another compatible model such as `deepseek-reasoner`.

## Notes

- The global hotkey format uses `pynput` syntax, for example `<ctrl>+t`.
- Some operating systems may require accessibility permissions for global hotkeys.
- Translation history is stored in `history.json`.
- Application logs are stored in `translator.log`.

## Test

```bash
pytest
```

