import os
import requests
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
# Ensure your key 'AIzaSyCoLeH_X4LEu30c-y8xOX7Upf_ykenQRxg' is in Render
API_KEY = os.environ.get("GOOGLE_API_KEY")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BUTTER OS | STABLE-PATH</title>
    <style>
        body { background: #ffffff; color: #1a1a1a; font-family: 'Courier New', monospace; margin: 0; display: flex; flex-direction: column; align-items: center; height: 100vh; overflow: hidden; }
        #bg-log { position: absolute; top: 0; left: 10px; font-size: 10px; color: rgba(0, 0, 0, 0.05); width: 100%; height: 100%; pointer-events: none; overflow: hidden; z-index: 1; }
        .hud-container { position: relative; display: flex; justify-content: center; align-items: center; flex: 1; width: 100%; z-index: 10; }
        #waveCanvas { position: absolute; width: 100%; height: 300px; display: none; filter: drop-shadow(0 0 12px #00d4ff); }
        .outer-ring { position: absolute; width: 340px; height: 340px; border: 1px dashed #e0e0e0; border-radius: 50%; animation: rotate 25s linear infinite; }
        .core { width: 100px; height: 100px; background: #00d4ff; border-radius: 50%; box-shadow: 0 0 40px rgba(0, 212, 255, 0.4); z-index: 10; }
        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        #status { margin-top: 20px; font-size: 0.8rem; letter-spacing: 5px; color: #0077ff; text-align: center; z-index: 10; font-weight: bold; }
        #mic-btn { width: 80px; height: 80px; border-radius: 50%; border: 2px solid #00d4ff; background: #ffffff; color: #00d4ff; font-size: 30px; margin-bottom: 60px; cursor: pointer; z-index: 20; transition: 0.3s; }
        #mic-btn.active-sys { background: #00d4ff; color: #fff; box-shadow: 0 0 30px rgba(0, 212, 255, 0.5); }
    </style>
</head>
<body>
    <div id="bg-log"></div>
    <div style="margin-top:50px; color:#cccccc; letter-spacing:10px; font-weight:bold; font-size: 0.7rem;">STABLE_V1_PATH</div>
    <div class="hud-container">
        <canvas id="waveCanvas"></canvas>
        <div class="outer-ring"></div>
        <div class="core" id="core"></div>
    </div>
    <div id="status">NEURAL_IDLE</div>
    <button id="mic-btn" onclick="toggleSystem()">⚡</button>

    <script>
        const canvas = document.getElementById('waveCanvas');
        const ctx = canvas.getContext('2d');
        const core = document.getElementById('core');
        const status = document.getElementById('status');
        const btn = document.getElementById('mic-btn');
        let isOnline = false;
        let animationId;

        function drawWave() {
            canvas.width = window.innerWidth;
            canvas.height = 300;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const time = Date.now() * 0.003;
            ctx.beginPath();
            ctx.lineWidth = 3;
            ctx.strokeStyle = '#00d4ff';
            for (let i = 0; i < canvas.width; i++) {
                const y = 150 + Math.sin(i * 0.015 + time) * 40 + Math.cos(i * 0.01 - time) * 15;
                ctx.lineTo(i, y);
            }
            ctx.stroke();
            animationId = requestAnimationFrame(drawWave);
        }

        async function speak(text, callback) {
            const synth = window.speechSynthesis;
            const phrases = text.split(/[.,!?;]/); 
            canvas.style.display = 'block';
            core.style.opacity = "0.2";
            drawWave();

            for (let phrase of phrases) {
                if (phrase.trim().length === 0) continue;
                await new Promise((resolve) => {
                    const utterance = new SpeechSynthesisUtterance(phrase);
                    const voices = synth.getVoices();
                    utterance.voice = voices.find(v => v.name.includes('Female')) || voices[0];
                    utterance.pitch = 1.3;
                    utterance.rate = 0.95;
                    utterance.onend = () => setTimeout(resolve, 450); // Human-like pause
                    synth.speak(utterance);
                });
            }
            canvas.style.display = 'none';
            core.style.opacity = "1";
            cancelAnimationFrame(animationId);
            if (callback) callback();
            if (isOnline) setTimeout(startListening, 600);
        }

        async function startListening() {
            if(!isOnline) return;
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.onstart = () => { status.innerText = "LISTENING..."; };
            recognition.onresult = async (event) => {
                const query = event.results[0][0].transcript;
                status.innerText = "PROCESSING...";
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    status.innerText = data.reply;
                    speak(data.reply);
                } catch (e) { status.innerText = "ERROR"; setTimeout(startListening, 1000); }
            };
            recognition.start();
        }

        function toggleSystem() {
            isOnline = !isOnline;
            if(isOnline) {
                btn.innerText = "✖";
                btn.classList.add('active-sys');
                speak("Hello Hiccup, system is online, bring it on.");
            } else {
                btn.innerText = "⚡";
                btn.classList.remove('active-sys');
                status.innerText = "NEURAL_IDLE";
                window.speechSynthesis.cancel();
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_CONTENT

@app.get("/ask")
async def ask(query: str):
    if not API_KEY:
        return {"reply": "Hiccup, I'm brainless. Check the Render Key!"}
    
    # SHIFTED TO STABLE V1 PATH
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
    params = {'key': API_KEY.strip()}
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"You are Butter, a witty female AI. Call Prawin Raja 'Hiccup'. Sarcastic, brief. Query: {query}"
            }]
        }]
    }
    
    try:
        response = requests.post(url, params=params, json=payload, timeout=15)
        data = response.json()
        if response.status_code == 200:
            return {"reply": data['candidates'][0]['content']['parts'][0]['text']}
        else:
            return {"reply": f"Hiccup, I'm hitting a wall: {data.get('error', {}).get('message', 'Path Error')}"}
    except Exception as e:
        return {"reply": "Static on the line, Hiccup."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
