import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
API_KEY = os.environ.get("GOOGLE_API_KEY")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FRIDAY | MARK VII</title>
    <style>
        body { background: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; flex-direction: column; align-items: center; height: 100vh; overflow: hidden; }
        
        /* THE HUD (HEADS-UP DISPLAY) */
        .hud-container { position: relative; display: flex; justify-content: center; align-items: center; flex: 1; width: 100%; }
        
        .outer-ring { position: absolute; width: 280px; height: 280px; border: 1px dashed #00d4ff; border-radius: 50%; animation: rotate 10s linear infinite; opacity: 0.3; }
        .inner-ring { position: absolute; width: 240px; height: 240px; border: 2px solid #00d4ff; border-top: 2px solid transparent; border-radius: 50%; animation: rotate 3s linear infinite; }
        
        .core { width: 160px; height: 160px; background: radial-gradient(circle, #00d4ff 0%, #0088aa 100%); border-radius: 50%; box-shadow: 0 0 50px rgba(0,212,255,0.4); z-index: 10; transition: 0.3s; }
        
        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        
        /* VOICE PULSE */
        .active-voice { animation: pulse 0.6s infinite ease-in-out !important; }
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 30px #00d4ff; }
            50% { transform: scale(1.1); box-shadow: 0 0 80px #00d4ff; }
            100% { transform: scale(1); box-shadow: 0 0 30px #00d4ff; }
        }

        #status { margin-top: 40px; font-size: 1rem; letter-spacing: 2px; color: #0088aa; text-transform: uppercase; font-weight: bold; text-align: center; width: 80%; }
        #mic-btn { width: 80px; height: 80px; border-radius: 50%; border: none; background: #000; color: white; font-size: 30px; margin-bottom: 50px; cursor: pointer; z-index: 20; box-shadow: 0 0 20px rgba(0,0,0,0.2); }
    </style>
</head>
<body>
    <div style="margin-top:40px; color:#ccc; letter-spacing:10px;">F.R.I.D.A.Y.</div>
    
    <div class="hud-container">
        <div class="outer-ring"></div>
        <div class="inner-ring"></div>
        <div class="core" id="core"></div>
    </div>

    <div id="status">INITIALIZING NEURAL LINK...</div>
    <button id="mic-btn" onclick="toggleSystem()">ON</button>

    <script>
        const core = document.getElementById('core');
        const status = document.getElementById('status');
        const btn = document.getElementById('mic-btn');
        let isSystemActive = false;

        function speak(text, callback) {
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.1;
            utterance.onstart = () => core.classList.add('active-voice');
            utterance.onend = () => {
                core.classList.remove('active-voice');
                if (callback) callback();
                if (isSystemActive) setTimeout(startListening, 500); // RE-ACTIVATE EARS AUTOMATICALLY
            };
            synth.speak(utterance);
        }

        async function startListening() {
            if(!isSystemActive) return;
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            
            recognition.onstart = () => { status.innerText = "LISTENING..."; };
            
            recognition.onresult = async (event) => {
                const query = event.results[0][0].transcript.toLowerCase();
                status.innerText = "ANALYZING...";
                
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    status.innerText = data.reply;

                    let url = null;
                    if (query.includes("youtube")) url = "https://www.youtube.com";
                    else if (query.includes("news")) url = "https://news.google.com";
                    else if (query.includes("whatsapp")) url = "https://web.whatsapp.com";
                    else if (query.includes("search") || query.includes("find")) url = "https://google.com/search?q=" + query;

                    speak(data.reply, () => {
                        if (url) window.open(url, '_blank'); // Opens in NEW TAB so Friday stays open
                    });
                } catch (e) {
                    status.innerText = "STARK SERVER ERROR. RETRYING...";
                    setTimeout(startListening, 1000);
                }
            };

            recognition.onerror = () => { if(isSystemActive) startListening(); };
            recognition.start();
        }

        function toggleSystem() {
            isSystemActive = !isSystemActive;
            if(isSystemActive) {
                btn.innerText = "OFF";
                btn.style.background = "#00d4ff";
                status.innerText = "ONLINE";
                speak("Systems online. How can I help, Sir?");
            } else {
                btn.innerText = "ON";
                btn.style.background = "#000";
                status.innerText = "OFFLINE";
                window.speechSynthesis.cancel();
            }
        }
    </script>
</body>
</html>
"""

@app.get("/ask")
async def ask(query: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": f"You are FRIDAY from Iron Man. Be witty and brief. Address Prawin Raja as Sir. Response: {query}"}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        # Added safety check for JSON structure
        if 'candidates' in data:
            reply = data['candidates'][0]['content']['parts'][0]['text']
        else:
            reply = "Sir, the neural feedback is scrambled. Please repeat."
        return {"reply": reply}
    except:
        return {"reply": "Connection unstable, Sir."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
