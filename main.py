import os
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

app = FastAPI()

API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY.strip())
    model = genai.GenerativeModel('gemini-3-flash-preview')

# This global variable tracks if we should be watching the hand
vision_active = "off"

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>BUTTER v5.5 | HANDS FREE</title>
    <style>
        :root { --neon: #008f11; --lab-white: #ffffff; }
        body { background: var(--lab-white); color: #1a1a1a; font-family: 'Segoe UI', sans-serif; margin: 0; overflow: hidden; display: flex; flex-direction: column; align-items: center; height: 100vh; }
        #hackerCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.1; }
        .hud-popup { position: absolute; top: 15%; background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); border: 2px solid var(--neon); padding: 20px 40px; border-radius: 50px; z-index: 100; text-align: center; }
        .hud-content { font-family: 'Courier New', monospace; font-size: 1rem; color: var(--neon); font-weight: bold; }
    </style>
</head>
<body>
    <canvas id="hackerCanvas"></canvas>
    <div class="hud-popup"><div class="hud-content" id="statusText">SAY "BUTTER"</div></div>

    <script>
        const statusText = document.getElementById('statusText');
        const synth = window.speechSynthesis;

        async function speak(text, callback) {
            const u = new SpeechSynthesisUtterance(text);
            const voices = synth.getVoices();
            u.voice = voices.find(v => v.name.includes('Neural')) || voices[0];
            u.onend = () => { if(callback) callback(); startWakeWord(); };
            synth.speak(u);
        }

        function startWakeWord() {
            const rec = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
            rec.onresult = (e) => {
                const query = e.results[0][0].transcript.toLowerCase();
                if(query.includes("butter")) {
                    speak("Go ahead, Hiccup.", startMainListener);
                } else { rec.start(); }
            };
            rec.start();
        }

        function startMainListener() {
            const rec = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
            rec.onresult = async (e) => {
                const q = e.results[0][0].transcript;
                
                // COMMANDS
                if(q.includes("observe my hand")) {
                    await fetch('/set_vision?state=on');
                    speak("Vision engaged. I'm watching your gestures.");
                    return;
                }
                if(q.includes("task completed")) {
                    await fetch('/set_vision?state=off');
                    speak("Vision released.");
                    return;
                }

                statusText.innerText = "THINKING...";
                const res = await fetch(`/ask?query=${encodeURIComponent(q)}`);
                const data = await res.json();
                speak(data.reply);
            };
            rec.start();
        }
        window.onclick = () => { speak("Butter v5.5 Hands-Free Online."); };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home(): return HTML_CONTENT

@app.get("/set_vision")
def set_vision(state: str):
    global vision_active
    vision_active = state
    return {"status": "updated"}

@app.get("/get_vision")
def get_vision():
    global vision_active
    return Response(content=vision_active, media_type="text/plain")

@app.get("/ask")
async def ask(query: str):
    response = model.generate_content(f"You are Butter v5.5, a professional partner for Prawin Raja (Hiccup). Answer: {query}")
    return {"reply": response.text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
