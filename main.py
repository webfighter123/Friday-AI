import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import uvicorn

app = FastAPI()

# 1. BRAIN CONFIGURATION
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)
# Using the specific model path to avoid 404 errors
model = genai.GenerativeModel('models/gemini-1.5-flash')

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FRIDAY | OS</title>
    <style>
        body { background: #ffffff; color: #1a1a1a; font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; flex-direction: column; align-items: center; height: 100vh; overflow: hidden; }
        #header { margin-top: 50px; font-size: 1.5rem; font-weight: 300; letter-spacing: 12px; color: #bbb; text-transform: uppercase; }
        
        .core-container { display: flex; flex-direction: column; justify-content: center; align-items: center; flex: 1; width: 100%; }
        .ring { width: 200px; height: 200px; border-radius: 50%; border: 1px solid #eee; display: flex; justify-content: center; align-items: center; position: relative; }
        .inner-core { width: 150px; height: 150px; background: radial-gradient(circle, #00d4ff 0%, #0088aa 100%); border-radius: 50%; box-shadow: 0 0 30px rgba(0,212,255,0.3); transition: 0.3s; }
        
        /* PULSE ANIMATION */
        .active { animation: pulse 1s infinite ease-in-out; }
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 20px rgba(0,212,255,0.3); }
            50% { transform: scale(1.1); box-shadow: 0 0 50px rgba(0,212,255,0.6); }
            100% { transform: scale(1); box-shadow: 0 0 20px rgba(0,212,255,0.3); }
        }

        #status-text { margin-top: 40px; font-size: 1rem; color: #444; text-align: center; width: 85%; min-height: 1.5rem; font-weight: 300; }
        #controls { margin-bottom: 60px; }
        #mic-btn { width: 80px; height: 80px; border-radius: 50%; border: none; background: #1a1a1a; color: white; font-size: 32px; cursor: pointer; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div id="header">FRIDAY</div>
    
    <div class="core-container">
        <div class="ring">
            <div class="inner-core" id="visualizer"></div>
        </div>
        <div id="status-text">System standing by, Sir.</div>
    </div>

    <div id="controls">
        <button id="mic-btn" onclick="startListening()">🎤</button>
    </div>

    <script>
        const visualizer = document.getElementById('visualizer');
        const status = document.getElementById('status-text');

        function speak(text, callback) {
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.1;
            utterance.pitch = 0.85;

            utterance.onstart = () => visualizer.classList.add('active');
            utterance.onend = () => {
                visualizer.classList.remove('active');
                if (callback) callback();
            };
            
            synth.speak(utterance);
        }

        async function startListening() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) return alert("Sir, this browser does not support the required voice protocols.");

            const recognition = new SpeechRecognition();
            recognition.start();
            status.innerText = "Listening...";

            recognition.onresult = async (event) => {
                const query = event.results[0][0].transcript.toLowerCase();
                status.innerText = "Analyzing: " + query;
                
                try {
                    const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    status.innerText = data.reply;

                    // AUTO-REDIRECT LOGIC
                    let redirectUrl = null;
                    if (query.includes("youtube")) redirectUrl = "https://www.youtube.com";
                    else if (query.includes("news")) redirectUrl = "https://news.google.com";
                    else if (query.includes("whatsapp")) redirectUrl = "whatsapp://send"; 
                    else if (query.includes("search") || query.includes("find")) {
                        redirectUrl = "https://www.google.com/search?q=" + encodeURIComponent(query);
                    }

                    speak(data.reply, () => {
                        if (redirectUrl) window.location.assign(redirectUrl);
                    });
                } catch (e) {
                    status.innerText = "Neural link failed, Sir.";
                }
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
    try:
        # Custom prompt for Prawin's preferences
        prompt = (
            "You are FRIDAY, the AI from Iron Man. You are witty, concise, and helpful. "
            "You are talking to Prawin Raja, a medical aspirant. Address him as 'Sir'. "
            "If he mentions launching an app, confirm that you are doing it now. "
            f"Command: {query}"
        )
        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Sir, the server reported an error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
