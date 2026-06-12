# Episode 05 — Your First Open-Source AI App: Building a Local Chatbot

## Video Script (Target: 20–25 minutes)

---

### HOOK — Cold Open [0:00–1:30]

**[ON CAMERA —مباشر, high energy]**

"What if I told you that in the next 15 minutes, you could have a fully functional AI chatbot running on YOUR hardware — no API keys, no monthly fees, no sending your data to anyone. Sounds too good? Stick around."

**[TEXT ON SCREEN: "Build a local AI chatbot in 15 minutes"]**

"Today we're building not ONE but TWO chatbots from scratch — a terminal-based one and a full web interface with streaming, model selection, and conversation memory. And the best part? Everything runs 100% offline on your machine after setup."

**[TRANSITION GRAPHIC]**

"I'm [Host Name], this is On The FarSide, and today — Episode 5 — we're making AI truly yours."

---

### SECTION 1: Why Local AI? [1:30–4:00]

**[ON CAMERA]**

"Let's talk about why you'd even want to run AI locally. There are three big reasons:"

**[TEXT ON SCREEN — three bullets appear one by one]**

"**One — Privacy.** When you use ChatGPT, your conversations go to OpenAI's servers. For some use cases — healthcare, legal, personal journaling — that's a non-starter."

"**Two — Cost.** API costs add up fast. If you're experimenting, building a side project, or running batch jobs, $0.02 per 1K tokens can become expensive. Once you have the hardware, local inference is free."

"**Three — Control.** You own the model. You can fine-tune it, modify it, run it offline on an airplane — no internet required."

**[B-ROLL — show Ollama website, Hugging Face model hub]**

"Today's tools: **Ollama** — which lets you run open-source models locally with one command — and **Gradio** — a Python library for building web UIs in minutes."

---

### SECTION 2: The Landscape of Local AI [4:00–6:30]

**[SCREEN RECORDING — Ollama.com]**

"Before we code, let's understand the landscape. Ollama is like `pip` but for AI models. Under the hood, it uses llama.cpp — an efficient C++ implementation that runs large language models on consumer hardware."

"Head to ollama.com and you'll find models like Llama 3.2, Mistral, Phi, Gemma — all open source, all runnable locally."

**[Show Hugging Face model hub — huggingface.co/models]**

"All these models come from Hugging Face — the GitHub of machine learning. You can browse thousands of models there. For today's demo, we're using llama3.2:3b — Llama 3.2 with 3 billion parameters. It runs great on 8GB RAM and doesn't require a GPU."

**[ON CAMERA]**

"Here's a quick mental model: 7B parameters needs about 4-5GB of RAM. 3B needs about 2-3GB. 1B runs on almost anything. Pick the biggest model your machine can handle."

---

### SECTION 3: Installing Ollama [6:30–8:30]

**[SCREEN RECORDING — terminal]**

"Alright, let's get started. Step one: install Ollama."

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows — download from https://ollama.com/download
```

"Once installed, open a terminal and pull our model:"

```bash
ollama pull llama3.2
```

"This downloads the model — it's about 2GB. Go grab some coffee."

**[While downloading — ON CAMERA]**

"If you already have Ollama installed, you can follow along with whatever model you have. The code works with ANY Ollama model."

**[Verify download]**

```bash
ollama list
```

"You should see llama3.2 with its size. Now let's verify it works:"

```bash
ollama run llama3.2 "Hello, are you running locally?"
```

"Beautiful. We're talking to a real LLM, running entirely on this machine. Let's build something fun with it."

---

### SECTION 4: Project Setup [8:30–10:00]

**[SCREEN RECORDING — terminal]**

"Let's set up our project:"

```bash
mkdir -p ~/local-chatbot/src
cd ~/local-chatbot
```

"Create a requirements file:"

```bash
pip install ollama gradio
```

"That's it. Two dependencies. The ollama Python library is the official client, and Gradio gives us a web UI."

**[ON CAMERA]**

"Here's the plan: first we're going to build a terminal chatbot — just you and the model in the terminal, with conversation history and colored output. Then we'll level it up with a proper web interface, streaming responses, a model picker, and a temperature slider. Both in one episode. Let's go."

---

### SECTION 5: Building the Terminal Chatbot [10:00–15:00]

**[SCREEN RECORDING — code editor + terminal]**

"First up — the terminal chatbot. I'm going to build this live, and you can follow along."

**[Type out src/01_simple_chatbot.py — explain as you go]**

"Step one — imports. We need the ollama client, and colorama for colored terminal output."

```python
import ollama
from datetime import datetime
```

"Step two — conversation memory. We store the full conversation history as a list of message dicts. Each message has a role — 'system', 'user', or 'assistant' — and content."

```python
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant running locally. Be concise and friendly."}
]
```

"Step three — the chat loop. We read user input, append it to history, get a response, append that, and print."

**[Live code the full loop]**

```python
while True:
    user_input = input("\nYou: ").strip()
    if user_input.lower() in ('quit', 'exit', 'q'):
        break

    conversation_history.append({"role": "user", "content": user_input})

    response = ollama.chat(model='llama3.2', messages=conversation_history)
    reply = response['message']['content']

    conversation_history.append({"role": "assistant", "content": reply})
    print(f"\nAssistant: {reply}")
```

"Step four — let's add colored output and a nicer interface."

**[Add colorama/fancy printing with colors, timestamps, and formatting]**

"Step five — let's run it:"

```bash
python src/01_simple_chatbot.py
```

**[LIVE DEMO — have a conversation with the bot]**

```
You: What's the difference between CPU and GPU inference?

Assistant: Great question! CPU inference uses your computer's...
```

"Notice — it remembers what we just asked. That's the conversation history at work. Every turn, we send the full context so the model has memory."

**[ON CAMERA]**

"That's our first chatbot — done. About 40 lines of Python. Now let's make it look professional."

---

### SECTION 6: The Gradio Web Interface [15:00–21:00]

**[SCREEN RECORDING — code editor]**

"Now for the fun part — a real web UI. Gradio is incredible for this. You write a Python function, and Gradio creates a full web interface around it."

"Type `02_gradio_chatbot.py`:"

**[Live code the script]**

"Step one — we need a function that takes a message and history, and returns a response. Gradio's ChatInterface calls this for every message."

```python
def chat_fn(message, history):
    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
    for human, ai in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": ai})
    messages.append({"role": "user", "content": message})

    response = ollama.chat(model='llama3.2', messages=messages)
    return response['message']['content']
```

"Step two — let's enable streaming. Instead of waiting for the full response, we get tokens as they're generated. For streaming, we use a generator function."

```python
def chat_fn_streaming(message, history, model_name='llama3.2', temperature=0.7):
    messages = build_messages(message, history)
    stream = ollama.chat(model=model_name, messages=messages, stream=True, options={'temperature': temperature})
    partial = ""
    for chunk in stream:
        partial += chunk['message']['content']
        yield partial
```

"Step three — let's add a model selector and temperature slider using gradio.Blocks."

**[Code the full UI with columns, dropdown for model, slider for temperature, chatbot component]**

"Step four — run it:"

```bash
python src/02_gradio_chatbot.py
```

"Gradio gives us a URL — usually http://127.0.0.1:7860. Let's open it."

**[LIVE DEMO — browser opens, shows Gradio UI]**

"Look at this! We have a full ChatGPT-style interface running on our machine. I can pick the model, adjust temperature — that controls creativity vs. determinism — and chat with streaming responses."

**[Type a question and show streaming]**

"See how it streams token by token? That's real-time generation from our local model."

---

### SECTION 7: Comparing Local vs ChatGPT [21:00–23:30]

**[SPLIT SCREEN — ChatGPT on left, our local bot on right]**

"Let's be honest about how local compares to ChatGPT."

**[ON CAMERA]**

**Advantages of local:**
- Zero cost after setup
- Complete privacy — your data never leaves
- Works offline
- You control the model
- Great for learning

**Advantages of ChatGPT:**
- More powerful — GPT-4 is significantly smarter than 3B models
- Faster response times on their infrastructure
- Better at complex reasoning, coding, math
- No hardware requirements on your end

**My honest take?** Use both. Use ChatGPT for heavy lifting. Use local for experimentation, privacy-sensitive work, and learning. They're complementary tools, not competitors."

**[Show a table on screen comparing latency, cost, quality, privacy]**

---

### SECTION 8: Deploying & Next Steps [23:30–25:00]

**[ON CAMERA]**

"So where do you go from here?"

**[TEXT ON SCREEN — appears one by one]**

"**Retrieval-Augmented Generation (RAG):** Feed your local model your own documents — PDFs, wikis, codebases — and chat with them. That's Episode 6 territory."

"**Fine-tuning:** You can fine-tune these models on your own data. Makes them experts in YOUR domain."

"**Embedding models:** Add semantic search to your app. Find relevant documents automatically."

"**Multi-model pipelines:** Chain models together — one for coding, one for writing, one for reasoning."

"All of this runs locally with Ollama and open-source models."

**[ON CAMERA]**

"That's it for today. Code for everything we built is in the description below. If you found this helpful, smash that subscribe button — we've got episodes on RAG, fine-tuning, and building AI agents coming up."

"Next week on Episode 6: we build a RAG-powered document Q&A system. You're not gonna miss it."

"I'll see you on the FarSide."

**[OUTRO MUSIC — end screen with subscribe + next episode]**

---

## Production Notes

- **B-Roll needed:** Ollama.com, Hugging Face, model parameter comparison charts
- **Graphics needed:** Comparison table (Local vs ChatGPT), code overlays
- **Demo checklist:**
  - [ ] Ollama installed with llama3.2 pulled
  - [ ] Terminal works for demo
  - [ ] Browser ready for Gradio demo
  - [ ] Backup screenshots in case of live demo failure
- **Code files:** All code is in the episode directory under src/
- **Thumbnail idea:** Terminal with green text + Gradio UI side by side, text "YOUR AI — YOUR MACHINE"
