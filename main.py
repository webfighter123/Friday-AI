import os
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# --- 1. CONFIGURATION (2026 STABLE) ---
API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY.strip())
    # Using the highest-speed preview model for 2026
    model = genai.GenerativeModel('gemini-3-flash-preview')

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BUTTER | APEX</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root { --neon: #00ff41; --bg: #050505; }
        body { background: var(--bg); color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; overflow: hidden; display: flex; flex-direction: column; align-items: center; height: 100vh; }
        
        /* HACKER BACKGROUND */
        #hackerCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.2; }
        #canvas3d { position: absolute; top: 0; left: 0; z-index: 5; pointer-events: none; }
        
        /* FLOATING HUD POPUP */
        .hud-popup { 
            position: absolute; top: 20%; 
            background: rgba(255, 255, 255, 0.05); 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 65, 0.3);
            padding: 15px 30px; border-radius: 15px;
            display: none; z-index: 100;
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.1);
            transition: 0.3s;
        }

        .hud-content { font-family: 'Courier New', monospace; font-size: 0.9rem; color: var(--neon); letter-spacing: 2px; }

        /* CONTROL BUTTON */
        #mic-btn { 
            position: absolute; bottom: 50px;
            width: 80px; height: 80px; border-radius: 50%; 
            border: 2px solid var(--neon); background: transparent; 
            color: var(--neon); font-size: 30px; cursor: pointer; 
            z-index: 200; transition: 0.4s;
        }
        #mic-btn.active { background: var(--neon); color: #000; box-shadow: 0 0 50px var(--neon); }

        #waveCanvas { position: absolute; bottom: 150px; width: 100%; height: 100px; display: none; z-index: 10; pointer-events: none; }
    </style>
</head>
<body>
    <canvas id="hackerCanvas"></canvas>
    <canvas id="canvas3d"></canvas>
    
    <div id="statusPopup" class="hud-popup">
        <div class="hud-content" id="popupText">INITIALIZING...</div>
    </div>

    <canvas id="waveCanvas"></canvas>
    <button id="mic-btn" onclick="toggleSystem()">⚡</button>

    <script>
        // --- HEX HACKER RAIN ---
        const hCanvas = document.getElementById('hackerCanvas');
        const hCtx = hCanvas.getContext('2d');
        let drops = [];
        function initHacker() {
            hCanvas.width = window.innerWidth; hCanvas.height = window.innerHeight;
            for(let i=0; i<Math.floor(hCanvas.width/20); i++) drops[i] = 1;
        }
        function drawHacker() {
            hCtx.fillStyle = "rgba(5, 5, 5, 0.1)"; hCtx.fillRect(0,0,hCanvas.width,hCanvas.height);
            hCtx.fillStyle = "#00ff41"; hCtx.font = "14px monospace";
            for(let i=0; i<drops.length; i++) {
                const hex = Math.floor(Math.random()*16).toString(16).toUpperCase();
                hCtx.fillText(hex, i*20, drops[i]*20);
                if(drops[i]*20 > hCanvas.height && Math.random() > 0.975) drops[i]=0;
                drops[i]++;
            }
        }
        initHacker(); setInterval(drawHacker, 30);

        // --- 3D NEURAL CORE ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('canvas3d'), alpha:true, antialias:true});
        renderer.setSize(window.innerWidth, window.innerHeight);
        const sphere = new THREE.Mesh(new THREE.IcosahedronGeometry(1.5, 1), new THREE.MeshBasicMaterial({color: 0x00ff41, wireframe:true, transparent:true, opacity:0.2}));
        scene.add(sphere); camera.position.z = 5;
        function animate() { requestAnimationFrame(animate); sphere.rotation.y += 0.005; renderer.render(scene, camera); }
        animate();

        // --- SPEECH & HUD LOGIC ---
        const popup = document.getElementById('statusPopup');
        const popupText = document.getElementById('popupText');
        let voice = null;
        const synth = window.speechSynthesis;

        function updateHUD(text, show=true) {
            popupText.innerText = text;
            popup.style.display = show ? 'block' : 'none';
        }

        function loadVoice() {
            const voices = synth.getVoices();
            voice = voices.find(v => v.name.includes('Neural') && v.name.includes('Female')) || 
                    voices.find(v => v.name.includes('Google US English')) || voices[0];
        }
        if (speechSynthesis.onvoiceschanged !== undefined) speechSynthesis.onvoiceschanged = loadVoice;
        loadVoice();

        async function speak(text, callback) {
            synth.cancel();
            const u = new SpeechSynthesisUtterance(text);
            u.voice = voice;
            u.pitch = 1.1; u.rate = 1.0;
            u.onstart = () => { document.getElementById('waveCanvas').style.display='block'; updateHUD("TRANSMITTING..."); };
            u.onend = () => { 
                document.getElementById('waveCanvas').style.display='none'; 
                updateHUD("READY", false);
                if(callback) callback(); 
                if(isOnline) startListening(); 
            };
            synth.speak(u);
        }

        let isOnline = false;
        function startListening() {
            if(!isOnline) return;
            const rec = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
            rec.onstart = () => { updateHUD("LISTENING..."); };
            rec.onresult = async (e) => {
                const q = e.results[0][0].transcript;
                updateHUD("SYNCING...");
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(q)}`);
                    const data = await res.json();
                    speak(data.reply);
                } catch(err) { updateHUD("LINK_FAIL"); setTimeout(startListening, 1000); }
            };
            rec.onerror = () => { if(isOnline) startListening(); };
            rec.start();
        }

        function toggleSystem() {
            isOnline = !isOnline;
            const btn = document.getElementById('mic-btn');
            if(isOnline) {
                btn.classList.add('active');
                speak("Neural link active. I'm here, Hiccup. Let's get to work.");
            } else {
                btn.classList.remove('active');
                synth.cancel();
                updateHUD("OFFLINE", false);
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
    if not API_KEY: return {"reply": "Key missing."}
    try:
        # CONSOLIDATED PERSONALITY: Pro-Neurosurgery Partner + Stark Logic
        prompt = (
            "You are 'Butter', a professional female AI partner. You are warm, brilliant, and call Prawin Raja 'Hiccup'. "
            "You are a medical research expert. Be humanly witty but supportive. "
            "Never be mean. Answer this query immediately and concisely: "
        )
        response = model.generate_content(f"{prompt} {query}")
        return {"reply": response.text}
    except:
        return {"reply": "The link flickered, Hiccup. Try that again."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
