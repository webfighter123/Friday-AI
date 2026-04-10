import os
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# --- 1. NEURAL CORE CONFIG ---
API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY.strip())
    model = genai.GenerativeModel('gemini-3-flash-preview')

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BUTTER v5.5 | VISION LINK</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root { --neon: #008f11; --lab-white: #ffffff; }
        body { background: var(--lab-white); color: #1a1a1a; font-family: 'Segoe UI', sans-serif; margin: 0; overflow: hidden; display: flex; flex-direction: column; align-items: center; height: 100vh; }
        
        /* WHITE HACKER BACKGROUND */
        #hackerCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.15; }
        #canvas3d { position: absolute; top: 0; left: 0; z-index: 5; pointer-events: none; }
        
        /* HUD POPUP */
        .hud-popup { 
            position: absolute; top: 10%; 
            background: rgba(255, 255, 255, 0.8); 
            backdrop-filter: blur(15px);
            border: 2px solid var(--neon);
            padding: 20px 40px; border-radius: 50px;
            z-index: 100; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            display: none;
        }
        .hud-content { font-family: 'Courier New', monospace; font-size: 1rem; color: var(--neon); font-weight: bold; letter-spacing: 2px; }
        .version { position: absolute; bottom: 10px; font-size: 0.6rem; color: #ccc; letter-spacing: 4px; }
    </style>
</head>
<body>
    <canvas id="hackerCanvas"></canvas>
    <canvas id="canvas3d"></canvas>
    
    <div id="popup" class="hud-popup">
        <div class="hud-content" id="statusText">NEURAL_IDLE</div>
    </div>

    <div class="version">BUTTER_OS_v5.5_STARK_VISION</div>

    <script>
        const statusText = document.getElementById('statusText');
        const popup = document.getElementById('popup');
        
        // --- HACKER BACKGROUND ---
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
                hCtx.fillText(Math.floor(Math.random()*10), i*20, drops[i]*20);
                if(drops[i]*20 > hCanvas.height && Math.random() > 0.98) drops[i]=0;
                drops[i]++;
            }
        }
        initHacker(); setInterval(drawHacker, 40);

        // --- 3D CORE ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('canvas3d'), alpha:true, antialias:true});
        renderer.setSize(window.innerWidth, window.innerHeight);
        const sphere = new THREE.Mesh(new THREE.IcosahedronGeometry(1.5, 1), new THREE.MeshBasicMaterial({color: 0x008f11, wireframe:true, transparent:true, opacity:0.1}));
        scene.add(sphere); camera.position.z = 5;
        function animate() { requestAnimationFrame(animate); sphere.rotation.y += 0.005; renderer.render(scene, camera); }
        animate();

        // --- SPEECH ENGINE ---
        const synth = window.speechSynthesis;
        async function speak(text, callback) {
            const u = new SpeechSynthesisUtterance(text);
            const voices = synth.getVoices();
            u.voice = voices.find(v => v.name.includes('Neural') && v.name.includes('Female')) || voices[0];
            u.onstart = () => { popup.style.display = 'block'; statusText.innerText = "BUTTER_SPEAKING"; };
            u.onend = () => { if(callback) callback(); startWakeWordListener(); };
            synth.speak(u);
        }

        // --- WAKE WORD & COMMANDS ---
        function startWakeWordListener() {
            const SpeechRecognition = window.webkitSpeechRecognition || window.Recognition;
            if (!SpeechRecognition) { statusText.innerText = "BROWSER_NOT_SUPPORTED"; return; }
            const rec = new SpeechRecognition();
            rec.onstart = () => { statusText.innerText = 'SAY "BUTTER"'; };
            rec.onresult = (e) => {
                if(e.results[0][0].transcript.toLowerCase().includes("butter")) {
                    speak("System active. What's the plan, Hiccup?", startMainListener);
                } else { rec.start(); }
            };
            rec.onerror = () => { rec.start(); };
            rec.start();
        }

        function startMainListener() {
            const SpeechRecognition = window.webkitSpeechRecognition || window.Recognition;
            const rec = new SpeechRecognition();
            rec.onresult = async (e) => {
                const query = e.results[0][0].transcript;
                
                if(query.toLowerCase().includes("observe my hand")) {
                    speak("Vision sensors engaged. I am watching your hand now. Close your fist to collapse tabs.");
                    return;
                }
                if(query.toLowerCase().includes("task completed")) {
                    speak("Vision link released. Great work on the study investigation, Hiccup.");
                    return;
                }

                statusText.innerText = "THINKING...";
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    speak(data.reply);
                } catch(err) { speak("Link error, Hiccup."); }
            };
            rec.start();
        }

        window.onclick = () => { 
            if(statusText.innerText === "NEURAL_IDLE") speak("Butter v5.5 Vision Link Online."); 
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_CONTENT

@app.get("/ask")
async def ask(query: str):
    if not API_KEY: return {"reply": "API Key Missing."}
    try:
        prompt = (
            "You are 'Butter' v5.5. You are an expert medical study assistant. "
            "You help Hiccup (Prawin Raja) with Class 12 and NEET prep. "
            "Be helpful, precise, and human-like. If he asks to organize tabs, "
            "explain how you are configuring his investigation screen. Query: "
        )
        response = model.generate_content(f"{prompt} {query}")
        return {"reply": response.text}
    except Exception as e:
        return {"reply": "System flicker. Try again?"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
