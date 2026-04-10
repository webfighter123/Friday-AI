import os
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# 1. SETUP THE BRAIN (The Professional Way)
API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY.strip())
    # We use 'gemini-1.5-flash' because the SDK knows exactly where to find it.
    model = genai.GenerativeModel('gemini-1.5-flash')

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BUTTER OS | FINAL BOSS</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body { background: #ffffff; color: #1a1a1a; font-family: 'Courier New', monospace; margin: 0; overflow: hidden; display: flex; flex-direction: column; align-items: center; height: 100vh; }
        #canvas3d { position: absolute; top: 0; left: 0; z-index: 5; pointer-events: none; }
        #bg-log { position: absolute; top: 10px; left: 10px; font-size: 10px; color: rgba(0,0,0,0.1); z-index: 1; }
        .hud-overlay { position: relative; flex: 1; display: flex; justify-content: center; align-items: center; width: 100%; z-index: 10; }
        #waveCanvas { position: absolute; width: 100%; height: 300px; display: none; filter: drop-shadow(0 0 10px #00d4ff); z-index: 11; }
        #status { margin-bottom: 20px; font-size: 0.8rem; letter-spacing: 5px; color: #0077ff; font-weight: bold; z-index: 20; text-transform: uppercase; }
        #mic-btn { width: 80px; height: 80px; border-radius: 50%; border: 2px solid #00d4ff; background: #fff; color: #00d4ff; font-size: 30px; margin-bottom: 50px; cursor: pointer; z-index: 30; transition: 0.4s; }
        #mic-btn.active-sys { background: #00d4ff; color: #fff; box-shadow: 0 0 40px rgba(0, 212, 255, 0.6); }
    </style>
</head>
<body>
    <div id="bg-log">CORE_STABILITY: MAXIMUM</div>
    <canvas id="canvas3d"></canvas>
    <div class="hud-overlay">
        <canvas id="waveCanvas"></canvas>
        <div id="status">NEURAL_IDLE</div>
    </div>
    <button id="mic-btn" onclick="toggleSystem()">⚡</button>

    <script>
        // --- 3D INTERFACE ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas3d'), alpha: true, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        const geometry = new THREE.IcosahedronGeometry(1.5, 1);
        const material = new THREE.MeshBasicMaterial({ color: 0x00d4ff, wireframe: true, transparent: true, opacity: 0.4 });
        const sphere = new THREE.Mesh(geometry, material);
        scene.add(sphere);
        camera.position.z = 5;

        function animate() {
            requestAnimationFrame(animate);
            sphere.rotation.y += 0.005;
            renderer.render(scene, camera);
        }
        animate();

        // --- HYPER-REALITY VOICE ---
        async function speak(text, callback) {
            const synth = window.speechSynthesis;
            const phrases = text.split(/[.,!?;]/);
            document.getElementById('waveCanvas').style.display = 'block';
            for (let phrase of phrases) {
                if (phrase.trim().length === 0) continue;
                await new Promise(r => {
                    const u = new SpeechSynthesisUtterance(phrase);
                    u.voice = synth.getVoices().find(v => v.name.includes('Female')) || synth.getVoices()[0];
                    u.pitch = 1.3; u.rate = 0.95;
                    u.onend = () => setTimeout(r, 450);
                    synth.speak(u);
                });
            }
            document.getElementById('waveCanvas').style.display = 'none';
            if (callback) callback();
            if (isOnline) startListening();
        }

        let isOnline = false;
        async function startListening() {
            if(!isOnline) return;
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            const rec = new SpeechRecognition();
            rec.onresult = async (e) => {
                const q = e.results[0][0].transcript;
                document.getElementById('status').innerText = "THINKING...";
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(q)}`);
                    const d = await res.json();
                    document.getElementById('status').innerText = d.reply;
                    speak(d.reply);
                } catch(err) {
                    document.getElementById('status').innerText = "LINK LOST";
                }
            };
            rec.start();
        }

        function toggleSystem() {
            isOnline = !isOnline;
            if(isOnline) {
                document.getElementById('mic-btn').classList.add('active-sys');
                speak("Hello Hiccup, system is online, bring it on.");
            } else {
                document.getElementById('mic-btn').classList.remove('active-sys');
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
        return {"reply": "Hiccup, I'm missing my API key."}
    
    try:
        # THE SDK CALL: This handles all the URL logic automatically
        response = model.generate_content(
            f"You are Butter, a sarcastic female AI. Call Prawin Raja 'Hiccup'. {query}",
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=100,
                temperature=0.7
            )
        )
        return {"reply": response.text}
    except Exception as e:
        # If even the SDK fails, it's a key issue, not a code issue
        return {"reply": f"Hiccup, even the professional bridge is blocked. Error: {str(e)[:50]}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
