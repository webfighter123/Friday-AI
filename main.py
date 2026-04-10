import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicornimport os
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
    <title>BUTTER OS | SENTIENCE</title>
    <style>
        body { background: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; flex-direction: column; align-items: center; height: 100vh; overflow: hidden; }
        
        /* HEADS-UP DISPLAY */
        .hud-container { position: relative; display: flex; justify-content: center; align-items: center; flex: 1; width: 100%; }
        
        .outer-ring { position: absolute; width: 340px; height: 340px; border: 1px dashed #e0e0e0; border-radius: 50%; animation: rotate 25s linear infinite; }
        .inner-ring { position: absolute; width: 280px; height: 280px; border: 2px solid #00d4ff; border-top: 2px solid #ffcc00; border-radius: 50%; animation: rotate 6s linear infinite reverse; }
        
        .core { width: 140px; height: 140px; background: radial-gradient(circle, #ffcc00 0%, #00d4ff 100%); border-radius: 50%; box-shadow: 0 0 40px rgba(0,212,255,0.3); z-index: 10; transition: 0.5s; }

        /* VOICE WAVE ANIMATION */
        .wave-container { position: absolute; display: none; width: 200px; height: 100px; align-items: center; justify-content: space-between; z-index: 11; }
        .bar { width: 8px; height: 20px; background: #ffcc00; border-radius: 4px; animation: bounce 0.5s ease-in-out infinite; }
        .bar:nth-child(2) { animation-delay: 0.1s; }
        .bar:nth-child(3) { animation-delay: 0.2s; }
        .bar:nth-child(4) { animation-delay: 0.3s; }

        @keyframes bounce { 
            0%, 100% { height: 20px; } 
            50% { height: 60px; filter: brightness(1.2); } 
        }
        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

        #status { margin-top: 20px; font-size: 0.8rem; letter-spacing: 5px; color: #bbb; text-transform: uppercase; text-align: center; min-height: 40px; }
        #mic-btn { width: 80px; height: 80px; border-radius: 50%; border: none; background: #1a1a1a; color: white; font-size: 30px; margin-bottom: 60px; cursor: pointer; z-index: 20; transition: 0.3s; }
        #mic-btn.active-sys { background: #ffcc00; color: #000; box-shadow: 0 0 40px rgba(255, 204, 0, 0.4); }
    </style>
</head>
<body>
    <div style="margin-top:50px; color:#f5f5f5; letter-spacing:20px; font-weight:bold; font-size: 0.7rem;">NEURAL INTERFACE</div>
    
    <div class="hud-container">
        <div class="outer-ring"></div>
        <div class="inner-ring"></div>
        <div class="core" id="core"></div>
        <div class="wave-container" id="wave">
            <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
        </div>
    </div>

    <div id="status">OFFLINE</div>
    <button id="mic-btn" onclick="toggleSystem()">ON</button>

    <script>
        const core = document.getElementById('core');
        const status = document.getElementById('status');
        const btn = document.getElementById('mic-btn');
        const wave = document.getElementById('wave');
        let isOnline = false;

        function speak(text, callback) {
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(text);
            
            // FEMALE VOICE PROTOCOL
            const voices = synth.getVoices();
            // Try to find a high-quality female voice (Google or Apple)
            utterance.voice = voices.find(v => v.name.includes('Female') || v.name.includes('Google US English') || v.name.includes('Samantha')) || voices[0];
            
            utterance.rate = 1.0;
            utterance.pitch = 1.25; 

            utterance.onstart = () => {
                core.style.opacity = "0.3";
                wave.style.display = "flex";
            };
            utterance.onend = () => {
                core.style.opacity = "1";
                wave.style.display = "none";
                if (callback) callback();
                if (isOnline) setTimeout(startListening, 600);
            };
            synth.speak(utterance);
        }

        async function startListening() {
            if(!isOnline) return;
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.onstart = () => { status.innerText = "Listening..."; };
            
            recognition.onresult = async (event) => {
                const query = event.results[0][0].transcript.toLowerCase();
                status.innerText = "Analyzing...";
                
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    status.innerText = data.reply;

                    let url = null;
                    if (query.includes("youtube")) url = "https://www.youtube.com";
                    else if (query.includes("whatsapp")) url = "https://web.whatsapp.com";
                    else if (query.includes("news")) url = "https://news.google.com";
                    else if (query.includes("search") || query.includes("neet")) url = "https://google.com/search?q=" + query;

                    speak(data.reply, () => {
                        if (url) window.open(url, '_blank');
                    });
                } catch (e) {
                    status.innerText = "Neural Spike. Try again.";
                    setTimeout(startListening, 1000);
                }
            };

            recognition.onerror = () => { if(isOnline) startListening(); };
            recognition.start();
        }

        function toggleSystem() {
            isOnline = !isOnline;
            if(isOnline) {
                btn.innerText = "OFF";
                btn.classList.add('active-sys');
                speak("Butter is online, Hiccup. I was getting bored anyway.");
            } else {
                btn.innerText = "ON";
                btn.classList.remove('active-sys');
                status.innerText = "OFFLINE";
                window.speechSynthesis.cancel();
            }
        }
        
        // Pre-load voices for the female protocol
        window.speechSynthesis.getVoices();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_CONTENT

@app.get("/ask")
async def ask(query: str):
    SAFE_KEY = API_KEY.strip() if API_KEY else None
    if not SAFE_KEY:
        return {"reply": "Hiccup, you forgot to plug in my API key in Render!"}

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={SAFE_KEY}"
    
    personality = (
        "You are 'Butter', a sentient, witty, and charming female AI. "
        "You call Prawin Raja 'Hiccup' exclusively. Be very realistic, human-like, and slightly sarcastic. "
        "Keep responses very brief and helpful. "
        f"Hiccup says: {query}"
    )
    
    payload = {"contents": [{"parts": [{"text": personality}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        data = response.json()
        if response.status_code == 200:
            return {"reply": data['candidates'][0]['content']['parts'][0]['text']}
        else:
            return {"reply": f"Hiccup, I'm hitting a {response.status_code} error. Google is being difficult."}
    except Exception as e:
        return {"reply": "Stark servers are down. Check your connection, Hiccup."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

app = FastAPI()
API_KEY = os.environ.get("GOOGLE_API_KEY")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BUTTER | Neural Link</title>
    <style>
        body { background: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; flex-direction: column; align-items: center; height: 100vh; overflow: hidden; }
        
        .hud-container { position: relative; display: flex; justify-content: center; align-items: center; flex: 1; width: 100%; }
        
        /* THE BUTTER CORE - SOFTER AMBER/BLUE GLOW */
        .outer-ring { position: absolute; width: 300px; height: 300px; border: 1px solid #f0f0f0; border-radius: 50%; animation: rotate 15s linear infinite; }
        .inner-ring { position: absolute; width: 250px; height: 250px; border: 2px solid #00d4ff; border-top: 2px solid #ffcc00; border-radius: 50%; animation: rotate 4s linear infinite reverse; }
        
        .core { width: 140px; height: 140px; background: radial-gradient(circle, #ffcc00 0%, #00d4ff 100%); border-radius: 50%; box-shadow: 0 0 40px rgba(0,212,255,0.3); z-index: 10; transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        
        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        
        /* EMOTIVE PULSE */
        .speaking { animation: breathe 0.8s infinite ease-in-out; border: 4px solid #ffcc00; }
        @keyframes breathe {
            0%, 100% { transform: scale(1); filter: brightness(1); }
            50% { transform: scale(1.1); filter: brightness(1.3); box-shadow: 0 0 60px #ffcc00; }
        }

        #status { margin-top: 30px; font-size: 0.9rem; letter-spacing: 3px; color: #888; text-transform: uppercase; text-align: center; width: 85%; min-height: 40px; }
        #mic-btn { width: 70px; height: 70px; border-radius: 50%; border: none; background: #1a1a1a; color: white; font-size: 25px; margin-bottom: 50px; cursor: pointer; z-index: 20; transition: 0.3s; }
        #mic-btn.on { background: #ffcc00; box-shadow: 0 0 20px #ffcc00; color: #000; }
    </style>
</head>
<body>
    <div style="margin-top:40px; color:#eee; letter-spacing:15px; font-weight:bold;">BUTTER</div>
    
    <div class="hud-container">
        <div class="outer-ring"></div>
        <div class="inner-ring"></div>
        <div class="core" id="core"></div>
    </div>

    <div id="status">Listening for you, Hiccup...</div>
    <button id="mic-btn" onclick="toggleButter()">ON</button>

    <script>
        const core = document.getElementById('core');
        const status = document.getElementById('status');
        const btn = document.getElementById('mic-btn');
        let active = false;

        function speak(text, callback) {
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(text);
            
            // Setting a slightly more feminine, clear tone
            utterance.rate = 1.05;
            utterance.pitch = 1.2; 

            utterance.onstart = () => core.classList.add('speaking');
            utterance.onend = () => {
                core.classList.remove('speaking');
                if (callback) callback();
                if (active) setTimeout(listen, 600); 
            };
            synth.speak(utterance);
        }

        async function listen() {
            if(!active) return;
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.onstart = () => { status.innerText = "Listening..."; };
            
            recognition.onresult = async (event) => {
                const query = event.results[0][0].transcript.toLowerCase();
                status.innerText = "Thinking...";
                
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    status.innerText = data.reply;

                    let url = null;
                    if (query.includes("youtube")) url = "https://www.youtube.com";
                    else if (query.includes("whatsapp")) url = "https://web.whatsapp.com";
                    else if (query.includes("news")) url = "https://news.google.com";
                    else if (query.includes("search") || query.includes("find")) url = "https://google.com/search?q=" + query;

                    speak(data.reply, () => {
                        if (url) window.open(url, '_blank');
                    });
                } catch (e) {
                    status.innerText = "Neural spike detected. Try again, Hiccup.";
                    setTimeout(listen, 1000);
                }
            };

            recognition.onerror = () => { if(active) listen(); };
            recognition.start();
        }

        function toggleButter() {
            active = !active;
            if(active) {
                btn.innerText = "OFF";
                btn.classList.add('on');
                speak("I'm awake, Hiccup. Missed me?");
            } else {
                btn.innerText = "ON";
                btn.classList.remove('on');
                status.innerText = "Zzz...";
                window.speechSynthesis.cancel();
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    # This ensures the server knows to show the Butter interface at the main URL
    return HTML_CONTENT

@app.get("/", response_class=HTMLResponse)
def home():
    # This ensures the server knows to show the Butter interface at the main URL
    return HTML_CONTENT

@app.get("/ask")
async def ask(query: str):
    # Ensure the API Key is actually loaded
    if not API_KEY:
        return {"reply": "Hiccup, you forgot to give me a brain! The API Key is missing in Render settings."}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    personality = (
        "You are 'Butter', a witty, sentient female AI companion. "
        "You call Prawin Raja 'Hiccup'. You are charming and brief. "
        f"Hiccup says: {query}"
    )
    
    payload = {"contents": [{"parts": [{"text": personality}]}]}
    
    try:
        # We add a longer timeout and check the status code
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            reply = data['candidates'][0]['content']['parts'][0]['text']
            return {"reply": reply}
        else:
            # This will tell us if it's an 'Invalid API Key' (400) or 'Overloaded' (429)
            return {"reply": f"Neural spike error {response.status_code}, Hiccup. Check the logs."}
            
    except Exception as e:
        return {"reply": f"Connection dropped: {str(e)}"}
