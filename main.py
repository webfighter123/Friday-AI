import os
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

app = FastAPI()

# --- NEURAL CORE ---
API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY.strip())
    model = genai.GenerativeModel('gemini-3-flash-preview')

vision_active = "off"

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>BUTTER v5.6 | PERSISTENCE</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root { --neon: #008f11; --lab-white: #ffffff; }
        body { background: var(--lab-white); color: #1a1a1a; font-family: 'Segoe UI', sans-serif; margin: 0; overflow: hidden; display: flex; flex-direction: column; align-items: center; height: 100vh; }
        #hackerCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.15; }
        #canvas3d { position: absolute; top: 0; left: 0; z-index: 5; pointer-events: none; }
        .hud-popup { 
            position: absolute; top: 10%; 
            background: rgba(255, 255, 255, 0.85); 
            backdrop-filter: blur(15px);
            border: 2px solid var(--neon);
            padding: 20px 40px; border-radius: 50px;
            z-index: 100; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .hud-content { font-family: 'Courier New', monospace; font-size: 1rem; color: var(--neon); font-weight: bold; letter-spacing: 2px; text-align: center; }
    </style>
</head>
<body>
    <canvas id="hackerCanvas"></canvas>
    <canvas id="canvas3d"></canvas>
    <div id="popup" class="hud-popup"><div class="hud-content" id="statusText">INITIALIZING NEURAL LINK...</div></div>

    <script>
        const statusText = document.getElementById('statusText');
        const synth = window.speechSynthesis;
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        let isSpeaking = false;

        async function speak(text) {
            isSpeaking = true;
            recognition.stop(); // Stop listening while talking to prevent self-triggering
            const u = new SpeechSynthesisUtterance(text);
            u.onend = () => { 
                isSpeaking = false;
                recognition.start(); 
            };
            synth.speak(u);
        }

        recognition.onresult = async (event) => {
            const result = event.results[event.results.length - 1][0].transcript.toLowerCase();
            statusText.innerText = "HEARD: " + result.toUpperCase();

            // VISION COMMANDS
            if (result.includes("observe my hand") || result.includes("vision on")) {
                await fetch('/set_vision?state=on');
                speak("Vision sensors engaged. I'm watching you, Hiccup.");
                return;
            }
            if (result.includes("task completed") || result.includes("vision off")) {
                await fetch('/set_vision?state=off');
                speak("Vision link released. Sensors offline.");
                return;
            }

            // CHAT LOGIC (Only if Butter is mentioned or in follow-up)
            if (result.includes("butter")) {
                const query = result.replace("butter", "").trim();
                if (query.length > 1) {
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    speak(data.reply);
                } else {
                    speak("Ready for command.");
                }
            }
        };

        recognition.onend = () => { if (!isSpeaking) recognition.start(); };
        
        window.onclick = () => { 
            loadVoice();
            recognition.start();
            speak("Butter v5.6 Persistent Link Active.");
        };

        function loadVoice() {
            window.speechSynthesis.getVoices();
        }

        // --- MATRIX THEME & 3D (Omitted for brevity, keep your existing canvas code) ---
    </script>
</body>
</html>
"""

@app.get("/set_vision")
def set_vision(state: str):
    global vision_active
    vision_active = state
    print(f"Vision state changed to: {state}")
    return {"status": "ok"}

@app.get("/get_vision")
def get_vision():
    global vision_active
    return Response(content=vision_active, media_type="text/plain")

@app.get("/ask")
async def ask(query: str):
    response = model.generate_content(f"You are Butter v5.6. Professional, supportive partner for Hiccup. Concise answer: {query}")
    return {"reply": response.text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
