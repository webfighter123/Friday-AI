import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import uvicorn

app = FastAPI()

# 1. THE BRAIN SETUP
# Make sure your Render Environment Variable is named GOOGLE_API_KEY
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# Using the updated model name to fix the 404 error
model = genai.GenerativeModel('models/gemini-1.5-flash')

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FRIDAY | Interface</title>
    <style>
        body { background: #050505; color: #00d4ff; font-family: 'Courier New', monospace; margin: 0; display: flex; flex-direction: column; height: 100vh; }
        #header { padding: 15px; text-align: center; border-bottom: 2px solid #00d4ff; box-shadow: 0 0 15px #00d4ff; font-size: 1.2rem; letter-spacing: 5px; }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; }
        .msg { padding: 12px; border-radius: 10px; max-width: 80%; line-height: 1.4; border: 1px solid rgba(0, 212, 255, 0.2); }
        .user { align-self: flex-end; background: rgba(0, 68, 85, 0.4); border-right: 4px solid #00d4ff; }
        .friday { align-self: flex-start; background: rgba(0, 212, 255, 0.05); border-left: 4px solid #00d4ff; }
        #input-area { padding: 20px; display: flex; gap: 10px; background: #000; border-top: 1px solid #004455; }
        input { flex: 1; background: #111; border: 1px solid #004455; color: #00d4ff; padding: 12px; outline: none; }
        button { background: #00d4ff; border: none; padding: 10px 20px; cursor: pointer; color: #000; font-weight: bold; }
    </style>
</head>
<body>
    <div id="header">F.R.I.D.A.Y. SYSTEM ONLINE</div>
    <div id="chat-container" id="chat"></div>
    <div id="input-area">
        <button onclick="startListening()" style="background: #111; color: #00d4ff; border: 1px solid #004455; font-size: 20px;">🎤</button>
        <input type="text" id="userInput" placeholder="Awaiting command, sir..." onkeypress="if(event.key==='Enter') send()">
        <button id="sendBtn" onclick="send()">SEND</button>
    </div>

    <script>
        // Friday's Voice (Text-to-Speech)
        function speak(text) {
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.1; 
            utterance.pitch = 0.9;
            synth.speak(utterance);
        }

        // Friday's Ears (Speech-to-Text)
        function startListening() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                alert("Sir, your browser does not support voice recognition.");
                return;
            }
            const recognition = new SpeechRecognition();
            recognition.start();
            recognition.onresult = (event) => {
                document.getElementById('userInput').value = event.results[0][0].transcript;
                send();
            };
        }

        async function send() {
            const input = document.getElementById('userInput');
            const chat = document.getElementById('chat-container');
            if(!input.value) return;

            const val = input.value;
            chat.innerHTML += `<div class="msg user">${val}</div>`;
            input.value = '';

            try {
                const res = await fetch(`/ask?query=${encodeURIComponent(val)}`);
                const data = await res.json();
                chat.innerHTML += `<div class="msg friday"><b>FRIDAY:</b> ${data.reply}</div>`;
                speak(data.reply); // Speak the answer
            } catch (err) {
                chat.innerHTML += `<div class="msg friday" style="color:red"><b>ERROR:</b> Critical system failure.</div>`;
            }
            chat.scrollTop = chat.scrollHeight;
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
        # 2. THE PERSONALITY (System Instructions)
        prompt = (
            "You are FRIDAY, the advanced AI assistant from Marvel's Iron Man. "
            "You are talking to your creator, Prawin Raja, a medical aspirant and scientist. "
            "Be witty, helpful, and professional. Always address him as 'Sir'. "
            f"User says: {query}"
        )
        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Sir, it appears there is a connection issue with the Google servers: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
