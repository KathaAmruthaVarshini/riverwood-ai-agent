# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests, base64, os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env if exists
load_dotenv()  # safe: will do nothing if no .env file

# Option A: read from env (recommended)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # from .env or environment
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID") or "21m00Tcm4TlvDq8ikWAM"

# Option B: quick hardcode (uncomment and replace keys if you don't use .env)
# OPENAI_API_KEY = "sk-REPLACE_WITH_YOUR_KEY"
# ELEVEN_API_KEY = "eleven_REPLACE_WITH_KEY"
# VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Initialize OpenAI client (new style)
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

# CORS: allow Live Server (or any local dev origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "Riverwood AI backend running"}

@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        # 1) Get AI text reply (use gpt-4o-mini if available, else gpt-3.5-turbo)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",   # or "gpt-3.5-turbo" if you do not have access
            messages=[
                {"role": "system", "content": "You are a warm friendly Riverwood assistant. Use casual Hindi-English mix if appropriate."},
                {"role": "user", "content": msg.message}
            ]
        )
        ai_reply = completion.choices[0].message.content

        # 2) Convert text → speech using ElevenLabs TTS (returns binary mp3)
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {"text": ai_reply, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
        audio_resp = requests.post(tts_url, headers=headers, json=payload, timeout=30)

        # handle ElevenLabs errors
        if audio_resp.status_code != 200:
            return {"error": f"ElevenLabs TTS failed: {audio_resp.status_code} {audio_resp.text}"}

        # 3) encode audio (binary) to base64 for safe transfer to browser
        audio_b64 = base64.b64encode(audio_resp.content).decode("utf-8")

        return {"reply": ai_reply, "audio": audio_b64}

    except Exception as e:
        # Provide helpful error info for debugging
        return {"error": str(e)}
