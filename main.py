import os
import requests
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
# Pulling the key from Render Environment Variables
API_KEY = os.environ.get("GOOGLE_API_KEY")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BUTTER OS | LAB-WHITE</title>
    <style>
        body { background: #ffffff; color: #1a1a1a; font-family: 'Courier New', monospace; margin: 0; display: flex; flex-direction: column; align-items: center; height: 100vh; overflow: hidden; }
        #bg-log { position: absolute; top: 0; left: 10px; font-size: 10px; color: rgba(0, 0, 0, 0.05); width: 100%; height: 100%; pointer-events: none; overflow: hidden; z-index: 1; }
        .hud-container { position: relative; display: flex; justify-content: center; align-items: center; flex: 1; width: 100%; z-index: 10; }
        
        /* THE NEON INTERFERENCE WAVE */
        #waveCanvas { position: absolute; width: 100%; height: 300px; display: none; filter: drop-shadow(0 0 10px #00d4ff); }
        
        .outer-ring { position: absolute; width: 340px; height: 340px; border: 1px dashed #e0e0e0; border-radius: 50%; animation: rotate 25s linear infinite; }
        .core { width: 100px; height: 100px; background: #00d4ff; border-radius: 50%; box-shadow: 0 0 40px rgba(0, 212, 255, 0.4); z-index: 10; transition: 0.5s; }

        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        #status { margin-top: 20px; font-size: 0.8rem; letter-spacing: 5px; color: #0077ff; text-align: center; z-index: 10; font-weight: bold; }
        #mic-btn { width: 80px; height: 80px; border-radius: 50%; border: 2px solid #00d4ff; background: #ffffff; color: #00d4ff; font-size: 30px; margin-bottom: 60px; cursor: pointer; z-index: 20; transition: 0.3s; }
        #mic-btn.active-sys { background: #00d4ff; color: #fff; box-shadow: 0 0 30px rgba(0, 212, 255, 0.5); }
    </style>
</head>
<body>
    <div id="bg-log"></div>
    <div style="margin-top:50px; color:#cccccc; letter-spacing:10px; font-weight:bold; font-size: 0.7rem;">SYSTEM_ACTIVE</div>
    
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

        function drawInterferenceWave() {
            canvas.width = window.innerWidth;
            canvas.height = 300;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const time = Date.now() * 0.002;
            const colors = ['#00d4ff', '#ff00ff', '#0077ff'];
            
            for (let j = 0; j < 3; j++) {
                ctx.beginPath();
                ctx.lineWidth = 1;
                ctx.strokeStyle = colors[j];
                ctx.globalAlpha = 0.5;
                
                for (let i = 0; i < canvas.width; i++) {
                    const wave1 = Math.sin(i * 0.01 + time + j) * 40;
                    const wave2 = Math.sin(i * 0.02 - time * 0.5) * 20;
                    const y = 150 + wave1 + wave2;
                    ctx.lineTo(i, y);
                }
                ctx.stroke();
            }
            animationId = requestAnimationFrame(drawInterferenceWave);
        }

        function speak(text, callback) {
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(text);
            const voices = synth.getVoices();
            utterance.voice = voices.find(v => v.name.includes('Female')) || voices[0];
            utterance.pitch = 1.3;

            utterance.onstart = () => {
                canvas.style.display = 'block';
                core.style.opacity = "0.3";
                drawInterferenceWave();
            };
            utterance.onend = () => {
                canvas.style.display = 'none';
                core.style.opacity = "1";
                cancelAnimationFrame(animationId);
                if (callback) callback();
                if (isOnline) setTimeout(startListening, 600);
            };
            synth.speak(utterance);
        }

        async function startListening() {
            if(!isOnline) return;
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.onstart = () => { status.innerText = "Listening..."; };
            recognition.onresult = async (event) => {
                const query = event.results[0][0].transcript;
                status.innerText = "Analyzing...";
                
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    status.innerText = data.reply;
                    speak(data.reply);
                } catch (e) {
                    status.innerText = "Neural Error";
                    setTimeout(startListening, 1000);
                }
            };
            recognition.onerror = () => { if(isOnline) startListening(); };
            recognition.start();
        }

        function toggleSystem() {
            isOnline = !isOnline;
            if(isOnline) {
                btn.innerText = "✖";
                btn.classList.add('active-sys');
                speak("Butter is online, Hiccup. Ready to dominate.");
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
        return {"reply": "Hiccup, check the Render Key. It's empty."}
    
    # THE 404 KILLER: This is the exact Google API path
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    params = {'key': API_KEY.strip()}
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"You are Butter, a sarcastic, witty female AI. Call Prawin Raja 'Hiccup'. Query: {query}"
            }]
        }]
    }
    
    try:
        # Using separate params and json fields to avoid URL mangling
        response = requests.post(url, params=params, json=payload, timeout=15)
        data = response.json()
        
        if response.status_code == 200:
            return {"reply": data['candidates'][0]['content']['parts'][0]['text']}
        else:
            # Butter will tell us exactly what's wrong now
            error_msg = data.get('error', {}).get('message', 'Unknown Protocol Error')
            return {"reply": f"Hiccup, I'm getting a {response.status_code}. It says: {error_msg}"}
    except Exception as e:
        return {"reply": f"Neural link snapped: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
