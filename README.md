# 🤖 JARVIS - AI Voice Assistant

A Python-based **AI voice assistant** that listens to voice commands, understands the user's requests using Ollama, and performs useful computer and web-related tasks.

## ✨ Features

- 🎤 Voice command recognition using SpeechRecognition
- 🔊 Voice responses using pyttsx3
- 🧠 AI-powered command understanding using Ollama
- 🌐 Live internet search
- 🔎 Google search
- ▶️ YouTube search
- 🌍 Open websites using voice commands
- 💻 Open Windows applications
- 💬 Normal AI conversation
- 🇮🇳 English, Hindi and Hinglish command support
- 🛑 Voice-controlled exit command

## 🧠 How JARVIS Works

JARVIS listens to the user's voice command, processes the request using AI, and performs the required action.

The assistant can handle different types of commands:

- 💬 `CHAT` — Normal AI conversation
- 🔎 `SEARCH_WEB` — Google search
- 🌐 `LIVE_SEARCH` — Current information and live web search
- ▶️ `PLAY_YOUTUBE` — Search and play YouTube content
- 🌍 `OPEN_WEBSITE` — Open websites
- 💻 `OPEN_APP` — Open Windows applications
- 🛑 `STOP` — Stop the assistant

## 🛠️ Technologies Used

- **Python**
- **SpeechRecognition**
- **pyttsx3**
- **Ollama**
- **DDGS**
- **Python Standard Library**

## 🚀 How to Run

### 1. Install Python

Make sure **Python 3** is installed on your computer.

Check your Python version:

```bash
python --version
````

### 2. Clone the Repository

```bash
git clone https://github.com/meet-vora-eng/JARVIS-AI-ASSISTANT.git
```

Open the project folder:

```bash
cd JARVIS-AI-ASSISTANT
```

### 3. Create a Virtual Environment

Before installing the project dependencies, create a virtual environment:

```bash
python -m venv .venv
```

This creates an isolated Python environment for JARVIS.

### 4. Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, you should see:

```text
(.venv)
```

at the beginning of your terminal.

### 5. Install Required Packages

Install all required Python packages:

```bash
pip install -r requirements.txt
```

### 6. Install and Set Up Ollama

JARVIS uses **Ollama** as its local AI engine.

Make sure Ollama is installed and running on your computer.

The current project uses:

```text
qwen3:1.7b
```

Make sure the model is available before running JARVIS.

### 7. Run JARVIS

Once everything is installed and the virtual environment is activated:

```bash
python main.py
```

JARVIS will start listening for voice commands.

## 🎤 Example Commands

You can say:

```text
What is Python?
```

```text
Search for artificial intelligence
```

```text
Play a song on YouTube
```

```text
Open Google
```

```text
Open Chrome
```

```text
Tell me the latest technology news
```

```text
Stop
```

## 🤖 AI Model

JARVIS currently uses **Ollama** with:

```text
qwen3:1.7b
```

## 📁 Project Structure

```text
JARVIS-AI-ASSISTANT/
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

> `.venv/` is used locally and is excluded from GitHub using `.gitignore`.

 📌 Project Status

Completed personal AI assistant project focused on **voice interaction, AI-powered command understanding, web search, and basic computer automation**.


**Built with Python by Meet Vora** 🚀

**Ye wala final rakh bhai.** Isme beginner ke liye complete setup flow bhi hai aur Snake-Water-Gun jaisa clean structure bhi. 🔥
```
