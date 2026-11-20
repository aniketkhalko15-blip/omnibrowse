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

ANTIGRAVITY_CHAT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Google Antigravity Mobile</title>
  <style>
    :root {
      --bg: #1e1e2e;
      --card-bg: #282a36;
      --sidebar-bg: #181825;
      --text: #f8f8f2;
      --accent: #bd93f9;
      --accent-glow: #bd93f940;
      --user-msg: #6272a4;
      --ai-msg: #44475a;
      --border: #44475a;
      --green: #50fa7b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
    
    /* Header */
    header { background: var(--sidebar-bg); border-bottom: 1px solid var(--border); padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; z-index: 10; }
    .brand { display: flex; align-items: center; gap: 8px; font-weight: bold; font-size: 16px; }
    .brand-icon { width: 14px; height: 14px; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px var(--green); }
    .model-badge { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 4px 8px; display: flex; align-items: center; }
    select { background: transparent; border: none; color: var(--text); font-size: 12px; font-weight: 600; outline: none; cursor: pointer; }
    
    /* Chat Container */
    #chat-viewport { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 14px; scroll-behavior: smooth; }
    .msg-group { display: flex; flex-direction: column; max-width: 88%; gap: 4px; }
    .msg-group.user { align-self: flex-end; align-items: flex-end; }
    .msg-group.bot { align-self: flex-start; align-items: flex-start; }
    
    .msg-header { font-size: 10px; color: #8be9fd; opacity: 0.8; margin-bottom: 2px; }
    .bubble { padding: 12px 16px; border-radius: 14px; font-size: 14px; line-height: 1.5; word-wrap: break-word; }
    .user .bubble { background: var(--user-msg); color: #fff; border-bottom-right-radius: 4px; }
    .bot .bubble { background: var(--ai-msg); color: var(--text); border: 1px solid var(--border); border-bottom-left-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    .bubble code { background: #181825; padding: 2px 5px; border-radius: 4px; font-family: monospace; font-size: 12px; color: #ff79c6; }
    
    .time { font-size: 9px; opacity: 0.6; margin-top: 3px; }
    
    /* Footer input */
    footer { background: var(--sidebar-bg); border-top: 1px solid var(--border); padding: 10px 14px; display: flex; gap: 8px; align-items: center; }
    .input-wrapper { flex: 1; display: flex; background: var(--card-bg); border: 1px solid var(--border); border-radius: 24px; padding: 6px 14px; align-items: center; }
    input[type="text"] { flex: 1; background: transparent; border: none; color: var(--text); font-size: 14px; outline: none; }
    .send-btn { width: 36px; height: 36px; border-radius: 50%; background: var(--accent); color: var(--bg); border: none; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: transform 0.1s; }
    .send-btn:active { transform: scale(0.92); }
    .send-btn svg { width: 16px; height: 16px; fill: var(--bg); }
    
    /* Loading typing indicator */
    .typing { display: none; gap: 4px; padding: 8px 12px; background: var(--ai-msg); border-radius: 12px; width: fit-content; }
    .dot { width: 6px; height: 6px; background: var(--text); border-radius: 50%; opacity: 0.4; animation: blink 1.2s infinite; }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes blink { 0%, 100% { opacity: 0.4; transform: scale(1); } 50% { opacity: 1; transform: scale(1.2); } }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="brand-icon"></div>
      <span>Antigravity</span>
    </div>
    <div class="model-badge">
      <select id="modelSelect">
        <option value="Claude 3.5 Sonnet">Claude 3.5 Sonnet</option>
        <option value="ChatGPT (GPT-4o)">ChatGPT (GPT-4o)</option>
        <option value="DeepSeek-V3" selected>DeepSeek-V3</option>
      </select>
    </div>
  </header>

  <div id="chat-viewport"></div>
  
  <div class="typing" id="typingIndicator" style="margin-left: 16px; margin-bottom: 8px;">
    <div class="dot"></div>
    <div class="dot"></div>
    <div class="dot"></div>
  </div>

  <footer>
    <div class="input-wrapper">
      <input type="text" id="msgInput" placeholder="Message Antigravity..." autocomplete="off">
    </div>
    <button class="send-btn" id="sendBtn" onclick="sendMessage()">
      <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
    </button>
  </footer>

  <script>
    const viewport = document.getElementById('chat-viewport');
    const input = document.getElementById('msgInput');
    const modelSelect = document.getElementById('modelSelect');
    const typing = document.getElementById('typingIndicator');

    async function fetchHistory() {
      try {
        const res = await fetch('/api/history');
        const data = await res.json();
        viewport.innerHTML = '';
        data.forEach(m => appendBubble(m.role, m.content, m.time, m.model));
        scrollToBottom();
      } catch (e) {
        console.error(e);
      }
    }

    function appendBubble(role, content, time, model) {
      const group = document.createElement('div');
      group.className = 'msg-group ' + (role === 'user' ? 'user' : 'bot');

      const header = document.createElement('div');
      header.className = 'msg-header';
      header.innerText = role === 'user' ? 'You' : (model || 'Antigravity');

      const bubble = document.createElement('div');
      bubble.className = 'bubble';
      bubble.innerHTML = content.replace(/\\n/g, '<br>');

      const timeEl = document.createElement('div');
      timeEl.className = 'time';
      timeEl.innerText = time || '';

      group.appendChild(header);
      group.appendChild(bubble);
      group.appendChild(timeEl);

      viewport.appendChild(group);
      scrollToBottom();
    }

    function scrollToBottom() {
      viewport.scrollTop = viewport.scrollHeight;
    }

    async function sendMessage() {
      const text = input.value.trim();
      if (!text) return;
      const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      appendBubble('user', text, now);
      input.value = '';
      typing.style.display = 'flex';
      scrollToBottom();

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, model: modelSelect.value })
        });
        const data = await res.json();
        typing.style.display = 'none';
        appendBubble('bot', data.response, now, modelSelect.value);
      } catch (err) {
        typing.style.display = 'none';
        appendBubble('bot', '⚠️ Error contacting server. Please retry.', now);
      }
    }

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') sendMessage();
    });

    fetchHistory();
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return ANTIGRAVITY_CHAT_HTML

@app.get("/api/history")
def history():
    return load_memory()

@app.post("/api/chat")
async def chat(req: MessageRequest):
    history_list = load_memory()
    now_str = datetime.now().strftime("%I:%M %p")

    # Record user message
    history_list.append({
        "role": "user",
        "content": req.message,
        "time": now_str,
        "model": req.model
    })

    # AI Execution logic (OmniBrowse or Agent)
    msg_lower = req.message.lower()
    if any(k in msg_lower for k in ["search", "google", "browse", "youtube", "gta"]):
        reply = f"I'm executing this in OmniBrowse right now: '{req.message}'. Checking live web elements..."
    else:
        reply = f"Hello Aniket! [{req.model}]: Memory is active and saved. How can I assist you with OmniBrowse or development today?"

    history_list.append({
        "role": "bot",
        "content": reply,
        "time": now_str,
        "model": req.model
    })

    save_memory(history_list)
    return {"response": reply}
