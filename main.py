import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import uvicorn

app = FastAPI()

# Securely get the API Key from Render's Environment Variables
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FRIDAY | OS</title>
    <style>
        body { background: #050505; color: #00d4ff; font-family: 'Courier New', monospace; margin: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        #header { padding: 15px; text-align: center; border-bottom: 2px solid #00d4ff; box-shadow: 0 0 15px #00d4ff; font-size: 1.2rem; letter-spacing: 5px; background: rgba(0,0,0,0.9); }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; background: radial-gradient(circle, #0a1a20 0%, #050505 100%); }
        .msg { padding: 12px 18px; border-radius: 10px; max-width: 80%; line-height: 1.4; border: 1px solid rgba(0, 212, 255, 0.3); }
        .user { align-self: flex-end; background: rgba(0, 68, 85, 0.5); color: #fff; border-right: 4px solid #00d4ff; }
        .friday { align-self: flex-start; background: rgba(0, 212, 255, 0.05); border-left: 4px solid #00d4ff; color: #00d4ff; }
        #input-area { padding: 20px; display: flex; gap: 10px; background: #000; border-top: 1px solid #004455; }
        input { flex: 1; background: #111; border: 1px solid #004455; color: #00d4ff; padding: 12px; border-radius: 5px; outline: none; }
        button { background: #00d4ff; border: none; padding: 10px 25px; cursor: pointer; color: #000; font-weight: bold; transition: 0.3s; }
        button:hover { background: #fff; box-shadow: 0 0 15px #00d4ff; }
    </style>
</head>
<body>
    <div id="header">F.R.I.D.A.Y. V1.1</div>
    <div id="chat-container" id="chat"></div>
    <div id="input-area">
        <input type="text" id="userInput" placeholder="Awaiting command, sir..." onkeypress="if(event.key==='Enter') send()">
        <button id="sendBtn" onclick="send()">EXECUTE</button>
    </div>
    <script>
        async function send() {
            const input = document.getElementById('userInput');
            const chat = document.getElementById('chat-container');
            const btn = document.getElementById('sendBtn');
            if(!input.value) return;

            const val = input.value;
            chat.innerHTML += `<div class="msg user">${val}</div>`;
            input.value = '';
            btn.innerText = "THINKING...";
            btn.disabled = true;

            try {
                // We use a relative path so it works on any URL
                const res = await fetch(`/ask?query=${encodeURIComponent(val)}`);
                const data = await res.json();
                chat.innerHTML += `<div class="msg friday"><b>FRIDAY:</b> ${data.reply}</div>`;
            } catch (err) {
                chat.innerHTML += `<div class="msg friday" style="color:red"><b>ERROR:</b> System connection lost.</div>`;
            }

            btn.innerText = "EXECUTE";
            btn.disabled = false;
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
        response = model.generate_content(f"You are FRIDAY, the advanced AI from Iron Man. Be concise, witty, and professional. Respond to: {query}")
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Sir, I encountered a core error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
