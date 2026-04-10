import os
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

app = FastAPI()

# --- 1. CONFIGURATION ---
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
    <title>BUTTER v5.5 | LAB EDITION</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root { --neon: #008f11; --lab-white: #ffffff; }
        body { background: var(--lab-white); color: #1a1a1a; font-family: 'Segoe UI', sans-serif; margin: 0; overflow: hidden; display: flex; flex-direction: column; align-items: center; height: 100vh; }
        #hackerCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.15; }
        #canvas3d { position: absolute; top: 0; left: 0; z-index: 5; pointer-events: none; }
        .hud-popup { 
            position: absolute; top: 10%; 
            background: rgba(255, 255, 255, 0.8); 
            backdrop-filter: blur(15px);
            border: 2px solid var(--neon);
            padding: 20px 40px; border-radius: 50px;
            z-index: 100; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .hud-content { font-family: 'Courier New', monospace; font-size: 1rem; color: var(--neon); font-weight: bold; letter-spacing: 2px; text-align: center; }
        .version { position: absolute; bottom: 10px; font-size: 0.6rem; color: #ccc; letter-spacing: 4px; }
    </style>
</head>
<body>
    <canvas id="hackerCanvas"></canvas>
    <canvas id="canvas3d"></canvas>
    <div id="popup" class="hud-popup">
        <div class="hud-content" id="statusText">CLICK TO SYNC NEURAL LINK</div>
    </div>
    <div class="version">BUTTER_OS_v5.5_LAB_STARK_VISION</div>

    <script>
        const statusText = document.getElementById('statusText');
        const synth = window.speechSynthesis;
        let femaleVoice = null;

        // --- THEME & 3D ---
        const hCanvas = document.getElementById('hackerCanvas');
        const hCtx = hCanvas.getContext('2d');
        let drops = [];
        function initHacker() {
            hCanvas.width = window.innerWidth; hCanvas.height = window.innerHeight;
            for(let i=0; i<Math.floor(hCanvas.width/20); i++) drops[i] = 1;
        }
        function drawHacker() {
            hCtx.fillStyle = "rgba(255, 255, 255, 0.2)"; hCtx.fillRect(0,0,hCanvas.width,hCanvas.height);
            hCtx.fillStyle = "#008f11"; hCtx.font = "15px monospace";
            for(let i=0; i<drops.length; i++) {
                const hex = Math.floor(Math.random()*16).toString(16).toUpperCase();
                hCtx.fillText(hex, i*20, drops[i]*20);
                if(drops[i]*20 > hCanvas.height && Math.random() > 0.98) drops[i]=0;
                drops[i]++;
            }
        }
        initHacker(); setInterval(drawHacker, 40);

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('canvas3d'), alpha:true, antialias:true});
        renderer.setSize(window.innerWidth, window.innerHeight);
        const sphere = new THREE.Mesh(new THREE.IcosahedronGeometry(1.5, 1), new THREE.MeshBasicMaterial({color: 0x008f11, wireframe:true, transparent:true, opacity:0.1}));
        scene.add(sphere); camera.position.z = 5;
        function animate() { requestAnimationFrame(animate); sphere.rotation.y += 0.005; renderer.render(scene, camera); }
        animate();

        // --- RECOGNITION GLOBAL ---
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        let recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        function loadVoice() {
            const v = synth.getVoices();
            femaleVoice = v.find(v => v.name.includes('Neural') && v.name.includes('Female')) || v[0];
        }
        speechSynthesis.onvoiceschanged = loadVoice;

        async function speak(text, callback) {
            synth.cancel();
            const u = new SpeechSynthesisUtterance(text);
            u.voice = femaleVoice;
            u.onstart = () => { statusText.innerText = "BUTTER_TRANSMITTING..."; };
            u.onend = () => { 
                if(callback) {
                    setTimeout(callback, 500); // Give the mic a break before restarting
                } else {
                    startWakeWord(); 
                }
            };
            synth.speak(u);
        }

        function startWakeWord() {
            recognition.onresult = (e) => {
                const q = e.results[0][0].transcript.toLowerCase();
                if(q.includes("butter")) {
                    recognition.stop();
                    speak("I'm here, Hiccup.", startMainListener);
                }
            };
            recognition.onend = () => { if(statusText.innerText === 'SAY "BUTTER"') recognition.start(); };
            statusText.innerText = 'SAY "BUTTER"';
            try { recognition.start(); } catch(e) {}
        }

        function startMainListener() {
            recognition.onresult = async (e) => {
                const query = e.results[0][0].transcript;
                recognition.stop();
                
                if(query.toLowerCase().includes("observe my hand")) {
                    await fetch('/set_vision?state=on');
                    speak("Vision engaged. Standing by.");
                    return;
                }
                if(query.toLowerCase().includes("task completed")) {
                    await fetch('/set_vision?state=off');
                    speak("Vision released.");
                    return;
                }

                statusText.innerText = "SYNCING WITH CORE...";
                const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                const data = await res.json();
                speak(data.reply);
            };
            statusText.innerText = "READY FOR COMMAND";
            recognition.start();
        }

        window.onclick = () => { 
            if(statusText.innerText.includes("CLICK")) {
                loadVoice();
                speak("Butter v5.5 Lab Edition Online.");
            }
        };
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
    prompt = "You are Butter v5.5. Expert medical assistant for Hiccup. Be concise: "
    response = model.generate_content(f"{prompt} {query}")
    return {"reply": response.text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
