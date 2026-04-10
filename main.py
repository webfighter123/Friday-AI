import os
import requests
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
# KEY: AIzaSyCoLeH_X4LEu30c-y8xOX7Upf_ykenQRxg
API_KEY = os.environ.get("GOOGLE_API_KEY")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BUTTER OS | OMNI-REPRESENTATION</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body { background: #ffffff; color: #1a1a1a; font-family: 'Courier New', monospace; margin: 0; overflow: hidden; display: flex; flex-direction: column; align-items: center; height: 100vh; }
        
        /* Kinetic HUD Elements */
        #canvas3d { position: absolute; top: 0; left: 0; z-index: 5; pointer-events: none; }
        #bg-log { position: absolute; top: 10px; left: 10px; font-size: 10px; color: rgba(0,0,0,0.1); z-index: 1; }
        
        .hud-overlay { position: relative; flex: 1; display: flex; justify-content: center; align-items: center; width: 100%; z-index: 10; }
        
        /* The Fluid Interference Wave */
        #waveCanvas { position: absolute; width: 100%; height: 300px; display: none; filter: drop-shadow(0 0 10px #00d4ff); z-index: 11; }
        
        .static-ring { position: absolute; width: 360px; height: 360px; border: 1px solid #f0f0f0; border-radius: 50%; z-index: 6; }
        
        #status { margin-bottom: 20px; font-size: 0.8rem; letter-spacing: 5px; color: #0077ff; font-weight: bold; z-index: 20; text-transform: uppercase; }
        
        #mic-btn { width: 80px; height: 80px; border-radius: 50%; border: 2px solid #00d4ff; background: #fff; color: #00d4ff; font-size: 30px; margin-bottom: 50px; cursor: pointer; z-index: 30; transition: 0.4s; box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
        #mic-btn.active-sys { background: #00d4ff; color: #fff; box-shadow: 0 0 40px rgba(0, 212, 255, 0.6); transform: scale(1.1); }
    </style>
</head>
<body>
    <div id="bg-log"></div>
    <canvas id="canvas3d"></canvas>
    
    <div style="margin-top:60px; color:#ddd; letter-spacing:15px; font-size:0.7rem; z-index: 20;">BUTTER_HYPER_REALITY_V3</div>

    <div class="hud-overlay">
        <canvas id="waveCanvas"></canvas>
        <div class="static-ring"></div>
        <div id="status">NEURAL_IDLE</div>
    </div>

    <button id="mic-btn" onclick="toggleSystem()">⚡</button>

    <script>
        // --- 1. 3D KINETIC CORE (Three.js) ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas3d'), alpha: true, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);

        const geometry = new THREE.IcosahedronGeometry(1.5, 1);
        const material = new THREE.MeshBasicMaterial({ color: 0x00d4ff, wireframe: true, transparent: true, opacity: 0.4 });
        const sphere = new THREE.Mesh(geometry, material);
        scene.add(sphere);
        camera.position.z = 5;

        // Interaction logic
        let mouseX = 0, mouseY = 0;
        document.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX - window.innerWidth / 2) / 100;
            mouseY = (e.clientY - window.innerHeight / 2) / 100;
        });

        function animate3D() {
            requestAnimationFrame(animate3D);
            sphere.rotation.y += 0.005;
            sphere.rotation.x += 0.002;
            sphere.position.x += (mouseX - sphere.position.x) * 0.05;
            sphere.position.y += (-mouseY - sphere.position.y) * 0.05;
            renderer.render(scene, camera);
        }
        animate3D();

        // --- 2. NEURAL VOICE ENGINE (Hyper-Reality) ---
        const waveCanvas = document.getElementById('waveCanvas');
        const wCtx = waveCanvas.getContext('2d');
        const btn = document.getElementById('mic-btn');
        const status = document.getElementById('status');
        let isOnline = false;
        let waveId;

        function drawWave() {
            waveCanvas.width = window.innerWidth;
            waveCanvas.height = 300;
            wCtx.clearRect(0, 0, waveCanvas.width, waveCanvas.height);
            const time = Date.now() * 0.004;
            wCtx.beginPath();
            wCtx.lineWidth = 2;
            wCtx.strokeStyle = '#00d4ff';
            for (let i = 0; i < waveCanvas.width; i++) {
                const y = 150 + Math.sin(i * 0.02 + time) * 50 + Math.cos(i * 0.01 - time) * 20;
                wCtx.lineTo(i, y);
            }
            wCtx.stroke();
            waveId = requestAnimationFrame(drawWave);
        }

        async function speak(text, callback) {
            const synth = window.speechSynthesis;
            const phrases = text.split(/[.,!?;]/);
            waveCanvas.style.display = 'block';
            sphere.material.opacity = 0.9;
            sphere.material.color.setHex(0x0077ff);
            drawWave();

            for (let phrase of phrases) {
                if (phrase.trim().length === 0) continue;
                await new Promise((resolve) => {
                    const utterance = new SpeechSynthesisUtterance(phrase);
                    const voices = synth.getVoices();
                    utterance.voice = voices.find(v => v.name.includes('Female')) || voices[0];
                    utterance.pitch = 1.3;
                    utterance.rate = 0.9;
                    utterance.onend = () => setTimeout(resolve, 500); // 500ms Human Pause
                    synth.speak(utterance);
                });
            }

            waveCanvas.style.display = 'none';
            sphere.material.opacity = 0.4;
            sphere.material.color.setHex(0x00d4ff);
            cancelAnimationFrame(waveId);
            if (callback) callback();
            if (isOnline) setTimeout(startListening, 600);
        }

        async function startListening() {
            if(!isOnline) return;
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.onstart = () => { status.innerText = "LISTENING_INPUT..."; };
            recognition.onresult = async (event) => {
                const query = event.results[0][0].transcript;
                status.innerText = "NEURAL_PROCESSING...";
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    status.innerText = data.reply;
                    speak(data.reply);
                } catch (e) { status.innerText = "LINK_FAULT"; setTimeout(startListening, 1000); }
            };
            recognition.start();
        }

        function toggleSystem() {
            isOnline = !isOnline;
            if(isOnline) {
                btn.innerText = "✖";
                btn.classList.add('active-sys');
                // Persisted Greeting
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
        return {"reply": "Hiccup, I'm missing my API key. Check Render settings!"}
    
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
    params = {'key': API_KEY.strip()}
    
    # SYSTEM PROMPT INJECTED WITH SARCASM AND MEMORY
    prompt = (
        "You are 'Butter', a witty, sentient female AI. "
        "You call Prawin Raja 'Hiccup' exclusively. Be sarcastic, sharp, and very human. "
        "Use short sentences. Use commas for natural pausing. "
        f"Hiccup says: {query}"
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, params=params, json=payload, timeout=15)
        data = response.json()
        if response.status_code == 200:
            return {"reply": data['candidates'][0]['content']['parts'][0]['text']}
        else:
            return {"reply": f"Hiccup, error {response.status_code}: {data.get('error', {}).get('message', 'Path snapped')}"}
    except Exception as e:
        return {"reply": "Neural spike detected, Hiccup. Try again."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
