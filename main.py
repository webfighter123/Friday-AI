import os
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
# This pulls the key you saved in Render's Environment Variables
API_KEY = os.environ.get("GOOGLE_API_KEY")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BUTTER OS | NEURAL INTERFACE</title>
    <style>
        body { background: #ffffff; color: #1a1a1a; font-family: 'Courier New', monospace; margin: 0; display: flex; flex-direction: column; align-items: center; height: 100vh; overflow: hidden; }
        
        #bg-log { position: absolute; top: 0; left: 10px; font-size: 10px; color: rgba(0, 0, 0, 0.05); width: 100%; height: 100%; pointer-events: none; overflow: hidden; z-index: 1; }
        
        .hud-container { position: relative; display: flex; justify-content: center; align-items: center; flex: 1; width: 100%; z-index: 10; }
        
        /* THE FLUID VOICE WAVE INTERFERENCE */
        .wave-canvas { position: absolute; width: 100%; height: 200px; display: none; opacity: 0.8; }
        
        .outer-ring { position: absolute; width: 340px; height: 340px; border: 1px dashed #e0e0e0; border-radius: 50%; animation: rotate 25s linear infinite; }
        
        .core { width: 100px; height: 100px; background: #00d4ff; border-radius: 50%; box-shadow: 0 0 40px rgba(0, 212, 255, 0.4); z-index: 10; transition: 0.5s; }

        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

        #status { margin-top: 20px; font-size: 0.8rem; letter-spacing: 5px; color: #0077ff; text-transform: uppercase; text-align: center; z-index: 10; }
        
        #mic-btn { width: 80px; height: 80px; border-radius: 50%; border: 2px solid #00d4ff; background: #ffffff; color: #00d4ff; font-size: 30px; margin-bottom: 60px; cursor: pointer; z-index: 20; transition: 0.3s; }
        #mic-btn.active-sys { background: #00d4ff; color: #fff; box-shadow: 0 0 30px rgba(0, 212, 255, 0.5); }
    </style>
</head>
<body>
    <div id="bg-log"></div>
    <div style="margin-top:50px; color:#cccccc; letter-spacing:20px; font-weight:bold; font-size: 0.7rem;">NEURAL_LINK_V1</div>
    
    <div class="hud-container">
        <canvas id="waveCanvas" class="wave-canvas"></canvas>
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

        // FLUID WAVE ANIMATION LOGIC
        function drawWave() {
            canvas.width = window.innerWidth;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.beginPath();
            ctx.lineWidth = 2;
            ctx.strokeStyle = '#00d4ff';
            
            const time = Date.now() * 0.005;
            for (let i = 0; i < canvas.width; i++) {
                const y = 100 + Math.sin(i * 0.02 + time) * 30 + Math.sin(i * 0.01 + time * 0.5) * 20;
                ctx.lineTo(i, y);
            }
            ctx.stroke();
            animationId = requestAnimationFrame(drawWave);
        }

        function speak(text, callback) {
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(text);
            const voices = synth.getVoices();
            utterance.voice = voices.find(v => v.name.includes('Female')) || voices[0];
            utterance.pitch = 1.25;

            utterance.onstart = () => {
                canvas.style.display = 'block';
                core.style.transform = 'scale(0.8)';
                drawWave();
            };
            utterance.onend = () => {
                canvas.style.display = 'none';
                core.style.transform = 'scale(1)';
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
                const query = event.results[0][0].transcript.toLowerCase();
                status.innerText = "Analyzing...";
                
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    status.innerText = data.reply;
                    speak(data.reply);
                } catch (e) {
                    status.innerText = "Error Connecting...";
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
                speak("Butter is online, Hiccup. Try not to break the code this time.");
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
    # Fixed 404 by using the precise v1beta endpoint structure
    if not API_KEY:
        return {"reply": "Hiccup, your API key is missing from Render's settings."}
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY.strip()}"
    
    personality = (
        "You are 'Butter', a sentient, witty, and charming female AI. "
        "You call Prawin Raja 'Hiccup' exclusively. Be sharp, sarcastic, and helpful. "
        f"Hiccup says: {query}"
    )
    
    payload = {"contents": [{"parts": [{"text": personality}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        data = response.json()
        if response.status_code == 200:
            return {"reply": data['candidates'][0]['content']['parts'][0]['text']}
        else:
            # Butter reports exactly why the neural link is failing
            return {"reply": f"Hiccup, I hit a {response.status_code} error. Google says: {data.get('error', {}).get('message', 'Link Fault')}"}
    except Exception as e:
        return {"reply": "Neural spike detected. Check your connection."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
