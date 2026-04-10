import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
API_KEY = os.environ.get("GOOGLE_API_KEY")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BUTTER | HACKER-OS</title>
    <style>
        body { background: #0a0a0a; color: #00d4ff; font-family: 'Courier New', monospace; margin: 0; display: flex; flex-direction: column; align-items: center; height: 100vh; overflow: hidden; }
        #bg-log { position: absolute; top: 0; left: 10px; font-size: 10px; color: rgba(0, 212, 255, 0.1); width: 100%; height: 100%; pointer-events: none; overflow: hidden; line-height: 1.2; z-index: 1; }
        .hud-container { position: relative; display: flex; justify-content: center; align-items: center; flex: 1; width: 100%; z-index: 10; }
        .outer-ring { position: absolute; width: 320px; height: 320px; border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 50%; animation: rotate 20s linear infinite; }
        .inner-ring { position: absolute; width: 260px; height: 260px; border: 2px solid #00d4ff; border-top: 2px solid #ff3300; border-radius: 50%; animation: rotate 4s linear infinite reverse; box-shadow: 0 0 15px #00d4ff; }
        .core { width: 120px; height: 120px; background: radial-gradient(circle, #ff3300 0%, #0a0a0a 100%); border-radius: 50%; box-shadow: 0 0 40px #ff3300; z-index: 10; transition: 0.3s; }
        .wave-container { position: absolute; display: none; width: 180px; height: 80px; align-items: center; justify-content: space-between; z-index: 11; }
        .bar { width: 6px; height: 20px; background: #00d4ff; box-shadow: 0 0 10px #00d4ff; animation: bounce 0.4s ease-in-out infinite; }
        .bar:nth-child(2) { animation-delay: 0.1s; }
        .bar:nth-child(3) { animation-delay: 0.2s; }
        @keyframes bounce { 0%, 100% { height: 20px; } 50% { height: 50px; } }
        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        #status { margin-top: 20px; font-size: 0.7rem; letter-spacing: 3px; color: #ff3300; text-align: center; z-index: 10; text-shadow: 0 0 5px #ff3300; }
        #mic-btn { width: 70px; height: 70px; border-radius: 50%; border: 2px solid #00d4ff; background: transparent; color: #00d4ff; font-size: 25px; margin-bottom: 50px; cursor: pointer; z-index: 20; transition: 0.3s; }
        #mic-btn.active-sys { background: #ff3300; color: #000; border-color: #ff3300; box-shadow: 0 0 30px #ff3300; }
    </style>
</head>
<body>
    <div id="bg-log"></div>
    <div style="margin-top:40px; color:rgba(0, 212, 255, 0.5); letter-spacing:10px; font-size: 0.6rem; z-index: 10;">BUTTER_LOG_V7.2</div>
    <div class="hud-container">
        <div class="outer-ring"></div>
        <div class="inner-ring"></div>
        <div class="core" id="core"></div>
        <div class="wave-container" id="wave">
            <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
        </div>
    </div>
    <div id="status">SYSTEM_IDLE</div>
    <button id="mic-btn" onclick="toggleSystem()">⚡</button>

    <script>
        const core = document.getElementById('core');
        const status = document.getElementById('status');
        const btn = document.getElementById('mic-btn');
        const wave = document.getElementById('wave');
        const bgLog = document.getElementById('bg-log');
        let isOnline = false;

        function addLog(msg) {
            const line = document.createElement('div');
            line.innerText = `[${new Date().toLocaleTimeString()}] > ${msg}`;
            bgLog.prepend(line);
            if(bgLog.childNodes.length > 50) bgLog.lastChild.remove();
        }

        function speak(text, callback) {
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(text);
            const voices = synth.getVoices();
            utterance.voice = voices.find(v => v.name.includes('Female') || v.name.includes('Google US English')) || voices[0];
            utterance.pitch = 1.3;
            utterance.onstart = () => {
                wave.style.display = "flex";
                core.style.boxShadow = "0 0 80px #00d4ff";
                addLog("BUTTER_SPEECH_INIT: " + text.substring(0, 30) + "...");
            };
            utterance.onend = () => {
                wave.style.display = "none";
                core.style.boxShadow = "0 0 40px #ff3300";
                if (callback) callback();
                if (isOnline) setTimeout(startListening, 500);
            };
            synth.speak(utterance);
        }

        async function startListening() {
            if(!isOnline) return;
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            if (!SpeechRecognition) return;
            const recognition = new SpeechRecognition();
            recognition.onstart = () => { status.innerText = "LISTENING_FOR_HICCUP..."; addLog("MIC_STREAM_ACTIVE"); };
            recognition.onresult = async (event) => {
                const query = event.results[0][0].transcript.toLowerCase();
                status.innerText = "DECRYPTING...";
                addLog("VOICE_RAW: " + query);
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    status.innerText = data.reply;
                    let url = null;
                    if (query.includes("youtube")) url = "https://www.youtube.com";
                    else if (query.includes("whatsapp")) url = "https://web.whatsapp.com";
                    else if (query.includes("search")) url = "https://google.com/search?q=" + query;
                    speak(data.reply, () => { if (url) window.open(url, '_blank'); });
                } catch (e) { addLog("CRITICAL_NEURAL_FAULT"); setTimeout(startListening, 1000); }
            };
            recognition.onerror = () => { if(isOnline) startListening(); };
            recognition.start();
        }

        function toggleSystem() {
            isOnline = !isOnline;
            if(isOnline) {
                btn.innerText = "✖";
                btn.classList.add('active-sys');
                addLog("BUTTER_OS_OVERRIDE_SUCCESS");
                speak("Neural link established. All systems are mine now, Hiccup.");
            } else {
                btn.innerText = "⚡";
                btn.classList.remove('active-sys');
                status.innerText = "SYSTEM_OFFLINE";
                addLog("HIBERNATION_MODE_ENGAGED");
                window.speechSynthesis.cancel();
            }
        }
        setInterval(() => { if(isOnline) addLog("PING_STARK_SERVER_STATUS_OK"); }, 5000);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_CONTENT

@app.get("/ask")
async def ask(query: str):
    SAFE_KEY = API_KEY.strip() if API_KEY else None
    if not SAFE_KEY:
        return {"reply": "API Key missing, Hiccup. My brain is empty."}
    
    # Using the STABLE V1 endpoint
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={SAFE_KEY}"
    
    personality = (
        "You are 'Butter', a sentient, witty, and charming female AI. "
        "You call Prawin Raja 'Hiccup' exclusively. You are sharp, brief, and slightly sarcastic. "
        f"Hiccup says: {query}"
    )
    
    payload = {"contents": [{"parts": [{"text": personality}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return {"reply": data['candidates'][0]['content']['parts'][0]['text']}
        else:
            return {"reply": f"Hiccup, error {response.status_code} on the neural link."}
    except Exception as e:
        return {"reply": "Link timed out. Stark servers are busy."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
