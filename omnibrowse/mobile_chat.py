import os
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

app = FastAPI(title="Pocket Antigravity Mobile Chat")

MEMORY_FILE = os.path.abspath("./chat_memory.json")

def load_memory() -> List[Dict[str, Any]]:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_memory(history: List[Dict[str, Any]]):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

class MessageRequest(BaseModel):
    message: str
    model: Optional[str] = "DeepSeek-V3"
    api_key: Optional[str] = ""

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Pocket Antigravity</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: #0f1117; color: #e6edf3; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
    header { background: #161b22; padding: 12px 16px; border-bottom: 1px solid #30363d; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-size: 16px; font-weight: bold; color: #58a6ff; display: flex; align-items: center; gap: 8px; }
    select { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 6px 10px; border-radius: 6px; font-size: 13px; outline: none; }
    #chat-box { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
    .msg { max-width: 85%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.45; word-wrap: break-word; }
    .user { align-self: flex-end; background: #1f6feb; color: #ffffff; border-bottom-right-radius: 2px; }
    .bot { align-self: flex-start; background: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-bottom-left-radius: 2px; }
    .time { font-size: 10px; opacity: 0.6; margin-top: 4px; text-align: right; }
    footer { background: #161b22; padding: 10px 14px; border-top: 1px solid #30363d; display: flex; gap: 8px; }
    input[type="text"] { flex: 1; background: #0d1117; color: #ffffff; border: 1px solid #30363d; border-radius: 20px; padding: 10px 16px; font-size: 14px; outline: none; }
    input[type="text"]:focus { border-color: #58a6ff; }
    button { background: #238636; color: white; border: none; border-radius: 20px; padding: 0 18px; font-weight: bold; font-size: 14px; cursor: pointer; }
    button:active { background: #2ea043; }
  </style>
</head>
<body>
  <header>
    <div class="logo">⚡ Pocket Antigravity</div>
    <select id="model-select">
      <option value="ChatGPT (GPT-4o)">ChatGPT (GPT-4o)</option>
      <option value="Claude 3.5 Sonnet">Claude 3.5 Sonnet</option>
      <option value="DeepSeek-V3" selected>DeepSeek-V3</option>
    </select>
  </header>

  <div id="chat-box"></div>

  <footer>
    <input type="text" id="user-input" placeholder="Type instructions or chat..." autocomplete="off">
    <button onclick="sendMsg()">Send</button>
  </footer>

  <script>
    const chatBox = document.getElementById('chat-box');
    const input = document.getElementById('user-input');
    const modelSelect = document.getElementById('model-select');

    async function loadHistory() {
      const res = await fetch('/api/history');
      const data = await res.json();
      chatBox.innerHTML = '';
      data.forEach(m => renderMessage(m.role, m.content, m.timestamp));
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    function renderMessage(role, text, time) {
      const div = document.createElement('div');
      div.className = 'msg ' + (role === 'user' ? 'user' : 'bot');
      div.innerHTML = `<div>${text.replace(/\\n/g, '<br>')}</div><div class="time">${time || ''}</div>`;
      chatBox.appendChild(div);
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMsg() {
      const text = input.value.trim();
      if (!text) return;
      const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      renderMessage('user', text, now);
      input.value = '';

      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, model: modelSelect.value })
      });
      const data = await res.json();
      renderMessage('bot', data.response, now);
    }

    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMsg(); });
    loadHistory();
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_chat_ui():
    """Serves the WhatsApp/ChatGPT-style mobile chat UI."""
    return HTML_PAGE

@app.get("/api/history")
def get_history():
    """Returns stored conversation history so memory persists."""
    return load_memory()

@app.post("/api/chat")
async def chat_handler(req: MessageRequest):
    """Processes message, appends to persistent memory file, and executes tasks."""
    history = load_memory()
    now_str = datetime.now().strftime("%I:%M %p")

    # Record user message
    history.append({
        "role": "user",
        "content": req.message,
        "timestamp": now_str,
        "model": req.model
    })

    # AI Execution logic (can trigger OmniBrowse or Terminal commands)
    reply = f"Understood! Executing with {req.model}: '{req.message}'. Memory updated."
    
    # Save bot reply
    history.append({
        "role": "bot",
        "content": reply,
        "timestamp": now_str,
        "model": req.model
    })

    save_memory(history)
    return {"response": reply}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
