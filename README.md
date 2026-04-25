# Academic English Translator

A desktop floating translation tool built with Python and PyQt5. The tool focuses on the translation of Chinese–English academic or professional texts and invokes the DeepSeek API using the OpenAI-compatible chat completion format.

## Features

- Integrates the DeepSeek API with a system prompt for academic translation  
- Automatically detects the language direction between Chinese and English  
- Supports clipboard paste functionality  

## Quick Start

1. Configure a **local Python environment or virtual environment**.  

   Visit the official Python website: `https://www.python.org/`  

   Select version **3.12**, download, and install.

2. Install dependencies:  

   Run the following command  

```bash
pip install -r requirements.txt
```

## Running the Program

```bash
python main.py
```

## Translation Model Configuration

Taking DeepSeek as an example, go to the DeepSeek open platform: `https://platform.deepseek.com/usage`  

Top up your balance and obtain an **API key** (sk-xxx...)

**API URL** `https://api.deepseek.com/chat/completions`

Select a model; it is recommended to use the latest DeepSeek v4 models:

**model**

- `deepseek-v4-flash`
- `deepseek-v4-pro`

If you need to use other compatible models, you can change the model parameters in the settings dialog.

Open **Settings** and fill in the corresponding parameters for **API Key**, **API URL**, and **model**.

Example:

> | API Key     | `sk-xxxxxx...`                              |
> | ----------- | ------------------------------------------- |
> | **API URL** | `https://api.deepseek.com/chat/completions` |
> | **model**   | `deepseek-v4-flash`                         |

## **Notes**

- The global hotkey format uses `pynput` syntax, for example `<ctrl>+t`.  
- Some operating systems may require granting accessibility permissions for global hotkeys.  
- Translation history is stored in the `history.json` file.  
- Application logs are stored in the `translator.log` file.

