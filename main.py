import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# 1. BRAIN CONFIGURATION
API_KEY = os.environ.get("GOOGLE_API_KEY")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FRIDAY | OS</title>
    <style>
        body { background: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; flex-direction: column; align-items: center; height: 100vh; overflow: hidden; }
        #header { margin-top: 50px; font-size: 1.2rem; font-weight: 300; letter-spacing: 15px; color: #ddd; text-transform: uppercase; }
        
        .core-container { display: flex; flex-direction: column; justify-content: center; align-items: center; flex: 1; width: 100%; }
        
        /* THE NEURAL CORE */
        .ring { width: 220px; height: 220px; border-radius: 50%; border: 1px solid #f0f0f0; display: flex; justify-content: center; align-items: center; position: relative; }
        .inner-core { width: 160px; height: 160px; background: radial-gradient(circle, #00d4ff 0%, #0088aa 100%); border-radius: 50%; box-shadow: 0 0 40px rgba(0,212,255,0.2); transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        
        /* PROCESSING & SPEAKING ANIMATIONS */
        .thinking { box-shadow: 0 0 80px rgba(0,212,255,0.8); transform: scale(0.9); }
        .active { animation: pulse 0.8s infinite ease-in-out; }
        
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 30px rgba(0,212,255,0.3); }
            50% { transform: scale(1.15); box-shadow: 0 0 70px rgba(0,212,255,0.6); }
            100% { transform: scale(1); box-shadow: 0 0 30px rgba(0,212,255,0.3); }
        }

        #status-text { margin-top: 50px; font-size: 1.1rem; color: #555; text-align: center; width: 80%; min-height: 3rem; font-weight: 300; line-height: 1.5; }
        #controls { margin-bottom: 70px; }
        #mic-btn { width: 85px; height: 85px; border-radius: 50%; border: none; background: #1a1a1a; color: white; font-size: 35px; cursor: pointer; box-shadow: 0 10px 30px rgba(0,0,0,0.1); transition: 0.3s; }
        #mic-btn:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.2); }
    </style>
</head>
<body>
    <div id="header">FRIDAY</div>
    <div class="core-container">
        <div class="ring"><div class="inner-core" id="visualizer"></div></div>
        <div id="status-text">Biometric scan complete. Standing by, Sir.</div>
    </div>
    <div id="controls"><button id="mic-btn" onclick="startListening()">🎤</button></div>

    <script>
        const visualizer = document.getElementById('visualizer');
        const status = document.getElementById('status-text');

        function speak(text, callback) {
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.15;
            utterance.pitch = 0.9;

            utterance.onstart = () => visualizer.classList.add('active');
            utterance.onend = () => {
                visualizer.classList.remove('active');
                if (callback) callback();
            };
            synth.speak(utterance);
        }

        async function startListening() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) return alert("Sir, neural voice protocols are restricted on this browser.");
            
            const recognition = new SpeechRecognition();
            recognition.start();
            status.innerText = "Listening...";
            visualizer.classList.add('thinking');

            recognition.onresult = async (event) => {
                visualizer.classList.remove('thinking');
                const query = event.results[0][0].transcript.toLowerCase();
                status.innerText = "Analyzing: " + query;
                
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    status.innerText = data.reply;

                    // ADVANCED AUTO-POPUP ENGINE
                    let redirectUrl = null;
                    if (query.includes("youtube")) redirectUrl = "https://www.youtube.com";
                    else if (query.includes("news")) redirectUrl = "https://news.google.com";
                    else if (query.includes("whatsapp")) redirectUrl = "whatsapp://send";
                    else if (query.includes("biology") || query.includes("neet") || query.includes("search")) {
                        redirectUrl = "https://www.google.com/search?q=" + encodeURIComponent(query);
                    }

                    // Speak response, then execute redirect
                    speak(data.reply, () => {
                        if (redirectUrl) {
                            status.innerText = "Redirecting to requested interface...";
                            window.location.assign(redirectUrl);
                        }
                    });
                } catch (e) { 
                    status.innerText = "Sir, the neural link has timed out.";
                    visualizer.classList.remove('active', 'thinking');
                }
            };
            
            recognition.onerror = () => {
                visualizer.classList.remove('thinking');
                status.innerText = "Awaiting command, Sir.";
            };
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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    "You are FRIDAY, the tactical AI for Prawin Raja. "
                    "He is a Medical Aspirant and Scientist. Address him as 'Sir'. "
                    "Your tone is sharp, witty, and high-tech. "
                    "If he asks to open something (YouTube, WhatsApp, News), confirm it wittily. "
                    "Keep responses very short (max 15 words) unless it's about biology. "
                    f"Command: {query}"
                )
            }]
        }]
    }
    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        reply = response_data['candidates'][0]['content']['parts'][0]['text']
        return {"reply": reply}
    except Exception as e:
        return {"reply": "Connection to the Stark servers is unstable, Sir."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
