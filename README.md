# 🌐 OmniBrowse

<p align="center">
  <b>The Universal Autonomous Browser Engine for AI Agents (ChatGPT, Claude, DeepSeek, Gemini & Local LLMs)</b>
</p>

<p align="center">
  <a href="https://github.com/aniketkhalko15-blip/omnibrowse/stargazers"><img src="https://img.shields.io/github/stars/aniketkhalko15-blip/omnibrowse?style=for-the-badge&logo=github&color=black" alt="GitHub stars"></a>
  <a href="https://instagram.com/aniket_aegistraton"><img src="https://img.shields.io/badge/Instagram-Follow%20@aniket__aegistraton-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram"></a>
  <a href="https://youtube.com/@yamiyugen"><img src="https://img.shields.io/badge/YouTube-Subscribe%20Yami%20Yugen-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" alt="License: MIT"></a>
</p>

---

## 👨‍💻 Created by Aniket
- 📸 **Instagram:** [@aniket_aegistraton](https://instagram.com/aniket_aegistraton)
- 🐙 **GitHub:** [@aniketkhalko15-blip](https://github.com/aniketkhalko15-blip)
- ▶️ **YouTube:** [Yami Yugen](https://youtube.com/@yamiyugen)

> *If you use OmniBrowse, please make sure to **Star the repo**, **Follow on Instagram**, and **Subscribe on YouTube** to support future updates!*

---

## ⚡ What is OmniBrowse?

**OmniBrowse** is a high-speed, lightweight browser engine built from the ground up for LLMs. Instead of drowning AI models in 50,000 lines of messy HTML, OmniBrowse extracts a **clean, indexed representation** of the page and equips your agents with deterministic tools to navigate, search, click, and extract data.

- 🧠 **Token Efficient:** Converts DOM into numbered element trees (`[1] <input> Search`, `[2] <button> Submit`), slashing context token costs by 80%.
- 🎯 **Universal LLM Support:** Compatible with Claude, OpenAI, DeepSeek, Gemini, and local models (Ollama / vLLM).
- 🛡️ **Anti-Bot Friendly:** Built-in stealth flags and human-like delays.
- 📸 **Multimodal Ready:** Fast viewport screenshotting for vision-enabled models.

---

## 🚀 Quickstart

### 1. Installation

```bash
git clone https://github.com/aniketkhalko15-blip/omnibrowse.git
cd omnibrowse
pip install -e .
playwright install chromium
```

### 2. Run the Demo

```bash
python examples/quickstart.py
```

---

## 💻 Example Usage

```python
import asyncio
from omnibrowse import OmniBrowser

async def run():
    browser = OmniBrowser(headless=False)
    await browser.start()

    # Navigate to any website
    state = await browser.goto("https://news.ycombinator.com")
    print(state["ai_view"])

    # AI clicks an element by ID
    await browser.click("1")

    # Close browser
    await browser.close()

asyncio.run(run())
```

---

## 📄 License
MIT License. Free to use and build upon.
