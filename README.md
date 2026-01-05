🎤 AI Voice Assistant

LangGraph • Llama 3.2 • IBM Watson • Flask

An intelligent voice-enabled AI assistant that listens to user speech, understands it using IBM Watson Speech-to-Text, processes queries via LangGraph + Llama 3.2 (Ollama), and replies back using IBM Watson Text-to-Speech — all through a modern web interface.

🚀 Features

🎙️ Voice Input (IBM Watson Speech-to-Text)

💬 Text Chat Mode

🤖 Local LLM (Llama 3.2 via Ollama)

🧠 LangGraph-based Agent Architecture

🔊 Voice Output (IBM Watson Text-to-Speech)

🌐 Modern Web UI (Tailwind CSS)

🔄 Session-based Conversation Memory

⚡ Streaming-ready Backend

🔐 Runs Locally — No Cloud LLM Cost

🧠 System Architecture
User (Voice / Text)
        ↓
IBM Watson STT
        ↓
Flask API
        ↓
LangGraph Agent
        ↓
Llama 3.2 (Ollama)
        ↓
Flask API
        ↓
IBM Watson TTS
        ↓
User (Voice Output)

🛠️ Tech Stack
Layer	Technology
Frontend	HTML, Tailwind CSS, JavaScript
Backend	Flask, Flask-CORS
AI Orchestration	LangGraph
LLM	Llama 3.2 (Ollama)
Speech-to-Text	IBM Watson STT
Text-to-Speech	IBM Watson TTS
Audio Handling	sounddevice, pygame
📁 Project Structure
ai-voice-assistant/
│
├── agent/
│   ├── llm.py        # Ollama LLM config & system prompt
│   ├── graph.py      # LangGraph agent definition
│   ├── stt.py        # IBM Watson Speech-to-Text
│   ├── tts.py        # IBM Watson Text-to-Speech
│
├── templates/
│   └── index.html    # Web UI
│
├── app.py            # Flask server & API routes
├── config.py         # API keys & URLs (ignored in git)
├── README.md
└── requirements.txt

🔧 Prerequisites
1️⃣ Install Ollama
https://ollama.com


Pull the model:

ollama pull llama3.2:3b


Verify:

ollama run llama3.2:3b

2️⃣ IBM Watson Credentials

Create an IBM Cloud account and enable:

Speech to Text

Text to Speech

Create config.py:

STT_API_KEY = "your_stt_api_key"
STT_URL = "your_stt_url"

TTS_API_KEY = "your_tts_api_key"
TTS_URL = "your_tts_url"


⚠️ Never commit config.py to GitHub

📦 Installation
git clone https://github.com/your-username/ai-voice-assistant.git
cd ai-voice-assistant

python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

▶️ Run the Application
python app.py


Open in browser:

http://localhost:5000

🗣️ Usage
🎤 Voice Mode

Click the microphone

Speak clearly

AI replies in voice + text

⌨️ Text Mode

Switch to Text

Type your query

Receive instant response

🧩 How It Works

User speaks → audio captured

IBM Watson STT converts speech to text

LangGraph agent processes the query

Llama 3.2 generates the response

IBM Watson TTS converts response to speech

Audio played in browser

🛡️ Key Design Decisions

AIMessage vs SystemMessage separation to ensure correct memory

Single system prompt injection for stability

Local LLM execution for privacy & speed

Threaded TTS to prevent UI blocking

🚧 Known Limitations

Requires microphone permission

IBM API rate limits apply

Streaming UI is optional (backend ready)

🌱 Future Enhancements

🔍 Web Search tool integration

📚 RAG with PDFs / Knowledge Base

🌎 Multilingual support

☁️ IBM watsonx.ai deployment

📱 Mobile-friendly UI

👩‍💻 Author

Sanchita Malakar
Computer Science Engineer | AI & Web Developer
📍 India

“Building practical AI systems, not just demos.”
