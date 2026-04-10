import os
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# 1. 2026 NEURAL CONFIGURATION
API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY.strip())
    # 2026 UPDATE: gemini-1.5 is dead. We use the Gemini 3 Flash engine.
    model = genai.GenerativeModel('gemini-3-flash-preview')

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BUTTER OS | 2026 EDITION</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body { background: #ffffff; color: #1a1a1a; font-family: 'Courier New', monospace; margin: 0; overflow: hidden; display: flex; flex-direction: column; align-items: center; height: 100vh; }
        #hackerCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; opacity: 0.1; }
        #canvas3d { position: absolute; top: 0; left: 0; z-index: 5; pointer-events: none; }
        .hud { position: relative; flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; width: 100%; z-index: 10; }
        #status { margin-top: 20px; font-size: 0.7rem; letter-spacing: 5px; color: #0077ff; font-weight: bold; text-transform: uppercase; }
        #mic-btn { width: 80px; height: 80px; border-radius: 50%; border: 2px solid #00d4ff; background: #fff; color: #00d4ff; font-size: 30px; cursor: pointer; z-index: 30; transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); margin-bottom: 50px; }
        #mic-btn.active { background: #00d4ff; color: #fff; box-shadow: 0 0 50px rgba(0, 212, 255, 0.5); transform: scale(1.1); }
        #waveCanvas { position: absolute; width: 100%; height: 200px; display: none; z-index: 11; opacity: 0.6; }
    </style>
</head>
<body>
    <canvas id="hackerCanvas"></canvas>
    <canvas id="canvas3d"></canvas>
    <div style="position:absolute; top:20px; letter-spacing:8px; font-size:0.6rem; color:#ccc; z-index:20;">CORE: GEMINI_3_FLASH</div>
    
    <div class="hud">
        <canvas id="waveCanvas"></canvas>
        <div id="status">NEURAL_IDLE</div>
    </div>

    <button id="mic-btn" onclick="toggleSystem()">⚡</button>

    <script>
        // --- WHITE MATRIX BACKGROUND ---
        const hCanvas = document.getElementById('hackerCanvas');
        const hCtx = hCanvas.getContext('2d');
        let drops = [];
        function initHacker() {
            hCanvas.width = window.innerWidth; hCanvas.height = window.innerHeight;
            for(let i=0; i<Math.floor(hCanvas.width/20); i++) drops[i] = 1;
        }
        function drawHacker() {
            hCtx.fillStyle = "rgba(255, 255, 255, 0.05)"; hCtx.fillRect(0,0,hCanvas.width,hCanvas.height);
            hCtx.fillStyle = "#d0d0d0"; hCtx.font = "15px monospace";
            for(let i=0; i<drops.length; i++) {
                const text = String.fromCharCode(Math.random()*128);
                hCtx.fillText(text, i*20, drops[i]*20);
                if(drops[i]*20 > hCanvas.height && Math.random() > 0.975) drops[i]=0;
                drops[i]++;
            }
        }
        initHacker(); setInterval(drawHacker, 40);

        // --- 3D CORE ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('canvas3d'), alpha:true, antialias:true});
        renderer.setSize(window.innerWidth, window.innerHeight);
        const sphere = new THREE.Mesh(new THREE.IcosahedronGeometry(1.5, 1), new THREE.MeshBasicMaterial({color: 0x00d4ff, wireframe:true, transparent:true, opacity:0.3}));
        scene.add(sphere); camera.position.z = 5;
        function animate() { requestAnimationFrame(animate); sphere.rotation.y += 0.005; sphere.rotation.x += 0.002; renderer.render(scene, camera); }
        animate();

        // --- SPEECH ENGINE ---
        async function speak(text, callback) {
            const synth = window.speechSynthesis;
            const u = new SpeechSynthesisUtterance(text);
            u.voice = synth.getVoices().find(v => v.name.includes('Female')) || synth.getVoices()[0];
            u.pitch = 1.2; u.rate = 1.0;
            u.onstart = () => { document.getElementById('waveCanvas').style.display = 'block'; };
            u.onend = () => { document.getElementById('waveCanvas').style.display = 'none'; if(callback) callback(); if(isOnline) startListening(); };
            synth.speak(u);
        }

        let isOnline = false;
        async function startListening() {
            if(!isOnline) return;
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            const rec = new SpeechRecognition();
            rec.onstart = () => { document.getElementById('status').innerText = "LISTENING..."; };
            rec.onresult = async (e) => {
                const query = e.results[0][0].transcript;
                document.getElementById('status').innerText = "THINKING...";
                const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                const data = await res.json();
                document.getElementById('status').innerText = data.reply;
                speak(data.reply);
            };
            rec.start();
        }

        function toggleSystem() {
            isOnline = !isOnline;
            const btn = document.getElementById('mic-btn');
            if(isOnline) {
                btn.classList.add('active');
                speak("Hello Hiccup. Gemini 3 core is online. Bring it on.");
            } else {
                btn.classList.remove('active');
                window.speechSynthesis.cancel();
                document.getElementById('status').innerText = "NEURAL_IDLE";
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
        return {"reply": "Hiccup, I'm missing my key. Check your Render Environment Variables."}
    
    try:
        # THE 2026 SDK CALL
        response = model.generate_content(
            f"You are Butter, a sarcastic, witty female AI. Call Prawin Raja 'Hiccup'. Be brief. Answer this: {query}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                max_output_tokens=150
            )
        )
        return {"reply": response.text}
    except Exception as e:
        # If gemini-3 fails, try the stable fallback gemini-2.5-flash
        try:
            fallback_model = genai.GenerativeModel('gemini-2.5-flash')
            res = fallback_model.generate_content(query)
            return {"reply": res.text}
        except:
            return {"reply": f"Hiccup, the 2026 firewall is too strong. Error: {str(e)[:40]}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
