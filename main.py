from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import uvicorn

app = FastAPI()

# --- CONFIGURATION ---
genai.configure(api_key="YOUR_API_KEY_HERE") # Ensure your key is here!
model = genai.GenerativeModel('gemini-pro')

# --- THE FACE (HTML/CSS) ---
HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>FRIDAY | Interface</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background-color: #0a0a0a; color: #00d4ff; font-family: 'Courier New', monospace; display: flex; flex-direction: column; height: 100vh; margin: 0; overflow: hidden; }
        #header { padding: 20px; text-align: center; border-bottom: 1px solid #00d4ff; box-shadow: 0 0 15px #00d4ff; font-weight: bold; letter-spacing: 5px; }
        #chat-box { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
        .msg { padding: 10px 15px; border-radius: 5px; max-width: 80%; line-height: 1.4; }
        .user { align-self: flex-end; background: #004455; color: white; }
        .friday { align-self: flex-start; border-left: 3px solid #00d4ff; background: rgba(0, 212, 255, 0.1); }
        #input-area { padding: 20px; display: flex; gap: 10px; border-top: 1px solid #00d4ff; }
        input { flex: 1; background: transparent; border: 1px solid #00d4ff; color: white; padding: 10px; outline: none; }
        button { background: #00d4ff; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div id="header">F.R.I.D.A.Y. SYSTEM ONLINE</div>
    <div id="chat-box" id="chat"></div>
    <div id="input-area">
        <input type="text" id="userQuery" placeholder="Speak, sir..." onkeypress="if(event.key==='Enter') sendQuery()">
        <button onclick="sendQuery()">SEND</button>
    </div>

    <script>
        async function sendQuery() {
            const input = document.getElementById('userQuery');
            const chat = document.getElementById('chat-box');
            if(!input.value) return;

            // Add User Message
            chat.innerHTML += `<div class="msg user">${input.value}</div>`;
            const query = input.value;
            input.value = '';

            // Ask Friday
            const response = await fetch(`/ask?query=${query}`);
            const data = await response.json();

            // Add Friday Response
            chat.innerHTML += `<div class="msg friday"><b>FRIDAY:</b> ${data.friday_says}</div>`;
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

# --- THE ROUTES ---
@app.get("/", response_class=HTMLResponse)
def get_ui():
    return HTML_CONTENT

@app.get("/ask")
def ask_friday(query: str):
    prompt = f"You are FRIDAY, Tony Stark's AI assistant. Give a concise, professional, yet slightly witty response to: {query}"
    response = model.generate_content(prompt)
    return {"friday_says": response.text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)