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
    <title>BUTTER v5.8 | STARK CLEAN</title>
    <style>
        :root { --neon: #008f11; --lab-white: #ffffff; }
        body { background: var(--lab-white); color: #1a1a1a; font-family: 'Segoe UI', sans-serif; margin: 0; overflow: hidden; display: flex; flex-direction: column; align-items: center; height: 100vh; }
        
        /* CLEAN HACKER THEME */
        #hackerCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.15; }
        
        .hud-popup { 
            position: absolute; top: 20%; 
            background: rgba(255, 255, 255, 0.9); 
            backdrop-filter: blur(10px);
            border: 2px solid var(--neon);
            padding: 25px 50px; border-radius: 50px;
            z-index: 100; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }
        .hud-content { font-family: 'Courier New', monospace; font-size: 1.2rem; color: var(--neon); font-weight: bold; letter-spacing: 2px; }
        .version { position: absolute; bottom: 15px; font-size: 0.7rem; color: #bbb; letter-spacing: 5px; z-index: 10; }
    </style>
</head>
<body>
    <canvas id="hackerCanvas"></canvas>
    
    <div id="popup" class="hud-popup">
        <div class="hud-content" id="statusText">CLICK TO ACTIVATE BUTTER</div>
    </div>

    <div class="version">BUTTER_OS_v5.8_STARK_LAB</div>

    <script>
        const statusText = document.getElementById('statusText');
        const synth = window.speechSynthesis;
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        
        if (!SpeechRecognition) {
            statusText.innerText = "BROWSER_NOT_SUPPORTED";
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        let isSpeaking = false;

        async function speak(text) {
            isSpeaking = true;
            recognition.stop();
            const u = new SpeechSynthesisUtterance(text);
            u.onend = () => { 
                isSpeaking = false; 
                try { recognition.start(); } catch(e) {}
            };
            synth.speak(u);
        }

        // --- THE DISPATCHER (OPENS SITES) ---
        function dispatch(query) {
            if (query.includes("youtube")) {
                speak("Opening YouTube, Hiccup.");
                window.open("https://www.youtube.com", "_blank");
                return true;
            }
            if (query.includes("google") || query.includes("search")) {
                speak("Accessing search engines.");
                window.open("https://www.google.com", "_blank");
                return true;
            }
            return false;
        }

        recognition.onresult = async (event) => {
            const result = event.results[event.results.length - 1][0].transcript.toLowerCase();
            statusText.innerText = result.toUpperCase();

            if (result.includes("butter")) {
                const query = result.replace("butter", "").trim();
                
                if (!dispatch(query)) {
                    if (query.length > 0) {
                        statusText.innerText = "THINKING...";
                        const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                        const data = await res.json();
                        speak(data.reply);
                    } else {
                        speak("I'm here, Hiccup.");
                    }
                }
            }
        };

        recognition.onend = () => { 
            if (!isSpeaking) {
                try { recognition.start(); } catch(e) {}
            }
        };
        
        window.onclick = () => { 
            if(statusText.innerText.includes("CLICK")) {
                statusText.innerText = 'SAY "BUTTER"';
                speak("Butter Online. System stabilized.");
                initHacker();
            }
        };

        // --- MATRIX RAIN THEME ---
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
                const char = Math.floor(Math.random()*10);
                hCtx.fillText(char, i*20, drops[i]*20);
                if(drops[i]*20 > hCanvas.height && Math.random() > 0.975) drops[i]=0;
                drops[i]++;
            }
        }
        setInterval(drawHacker, 45);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home(): return HTML_CONTENT

@app.get("/ask")
async def ask(query: str):
    if not API_KEY: return {"reply": "API Key Missing."}
    response = model.generate_content(f"You are Butter. Professional medical study assistant for Prawin Raja. Answer shortly: {query}")
    return {"reply": response.text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
