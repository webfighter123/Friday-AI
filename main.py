import os
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

app = FastAPI()

# --- NEURAL CORE ---
API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY.strip())
    model = genai.GenerativeModel('gemini-3-flash-preview')

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>BUTTER v5.7 | DISPATCHER</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root { --neon: #008f11; --lab-white: #ffffff; }
        body { background: var(--lab-white); color: #1a1a1a; font-family: 'Segoe UI', sans-serif; margin: 0; overflow: hidden; display: flex; flex-direction: column; align-items: center; height: 100vh; }
        #hackerCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.15; }
        #canvas3d { position: absolute; top: 0; left: 0; z-index: 5; pointer-events: none; }
        .hud-popup { 
            position: absolute; top: 10%; 
            background: rgba(255, 255, 255, 0.85); 
            backdrop-filter: blur(15px);
            border: 2px solid var(--neon);
            padding: 20px 40px; border-radius: 50px;
            z-index: 100; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .hud-content { font-family: 'Courier New', monospace; font-size: 1rem; color: var(--neon); font-weight: bold; letter-spacing: 2px; text-align: center; }
    </style>
</head>
<body>
    <canvas id="hackerCanvas"></canvas>
    <canvas id="canvas3d"></canvas>
    <div id="popup" class="hud-popup"><div class="hud-content" id="statusText">CLICK TO SYNC NEURAL LINK</div></div>

    <script>
        const statusText = document.getElementById('statusText');
        const synth = window.speechSynthesis;
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = true;
        recognition.interimResults = false;

        async function speak(text) {
            recognition.stop();
            const u = new SpeechSynthesisUtterance(text);
            u.onend = () => { recognition.start(); };
            synth.speak(u);
        }

        // --- THE DISPATCHER (OPENING APPS/SITES) ---
        function dispatch(query) {
            if (query.includes("youtube")) {
                speak("Opening YouTube for your investigation, Hiccup.");
                window.open("https://www.youtube.com", "_blank");
                return true;
            }
            if (query.includes("google") || query.includes("search")) {
                speak("Accessing global data streams.");
                window.open("https://www.google.com", "_blank");
                return true;
            }
            if (query.includes("notes") || query.includes("study")) {
                speak("Opening your study environment.");
                window.open("https://keep.google.com", "_blank");
                return true;
            }
            return false;
        }

        recognition.onresult = async (event) => {
            const result = event.results[event.results.length - 1][0].transcript.toLowerCase();
            statusText.innerText = "LINK_HEARD: " + result.toUpperCase();

            if (result.includes("butter")) {
                const query = result.replace("butter", "").trim();
                
                // Check if it's an app command first
                if (!dispatch(query)) {
                    // If not an app command, ask the AI
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    speak(data.reply);
                }
            }
        };

        recognition.onend = () => { recognition.start(); };
        
        window.onclick = () => { 
            recognition.start();
            speak("Butter v5.7 Dispatcher Online.");
            initHacker(); // Start the background theme
            animate();    // Start 3D
        };

        // --- MATRIX THEME ---
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
                if(drops[i]*20 > hCanvas.height && Math.random() > 0.985) drops[i]=0;
                drops[i]++;
            }
        }
        setInterval(drawHacker, 40);

        // --- 3D CORE ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('canvas3d'), alpha:true, antialias:true});
        renderer.setSize(window.innerWidth, window.innerHeight);
        const sphere = new THREE.Mesh(new THREE.IcosahedronGeometry(1.5, 1), new THREE.MeshBasicMaterial({color: 0x008f11, wireframe:true, transparent:true, opacity:0.1}));
        scene.add(sphere); camera.position.z = 5;
        function animate() { requestAnimationFrame(animate); sphere.rotation.y += 0.005; renderer.render(scene, camera); }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home(): return HTML_CONTENT

@app.get("/ask")
async def ask(query: str):
    prompt = "You are Butter v5.7. A professional medical AI partner for Hiccup. Concise answer: "
    response = model.generate_content(f"{prompt} {query}")
    return {"reply": response.text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
