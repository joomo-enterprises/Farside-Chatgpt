# Episode 03: Multimodal AI Explained — GPT-4o vs Gemini 2.5 Pro vs Claude Opus 4.1

**Series:** On The FarSide Series  
**Runtime:** ~22 minutes  
**Style:** Dark slate + Orange + White  
**Format:** Talking head + screen recordings + comparison graphics

---

## TIMESTAMPS & SCRIPT

---

### [0:00–0:45] COLD OPEN / HOOK

**[VISUAL: Fast-cut montage — GPT-4o logo, Gemini logo, Claude logo flashing on screen with audio waveforms, image grids, and code snippets. High-energy music bed.]**

**HOST (V.O.):**  
"GPT-4o, Gemini, and Claude all process text, images, and audio — but they do it VERY differently."

**[VISUAL: Split screen — three AI models side by side, each processing a different modality in real-time animation.]**

**HOST (V.O.):**  
"One of them hears you speak and responds in under half a second. One of them can read two million tokens of context — that's like feeding it an entire codebase in a single prompt. And one of them will reason through a complex multi-step problem like a senior engineer."

**[VISUAL: Host appears on camera. Dark slate background, orange accent lighting.]**

**HOST (ON CAMERA):**  
"Today, we're going deep on multimodal AI. What it actually means, how these three models handle it under the hood, and — most importantly — which one gives you the most bang for your buck. Stick around for the live demo where we run the exact same prompt across all three."

**[VISUAL: Episode title card — "Multimodal AI Exploded" with orange glow effect.]**

---

### [0:45–3:30] SEGMENT 1: WHAT IS MULTIMODAL AI?

**[VISUAL: Animated diagram — a brain with labeled inputs: text, image, audio, video flowing in.]**

**HOST (V.O.):**  
"Let's start with the basics. 'Multimodal' literally means 'multiple modes' or 'multiple modalities.' In AI, it refers to a model that can understand and generate more than just text."

**[VISUAL: Timeline graphic showing AI evolution.]**

**HOST (V.O.):**  
"Think about it this way: early language models were text-in, text-out. You type words, you get words back. That was 2020, 2021. Then came image understanding — you could upload a photo and ask about it. That was a game changer."

**[VISUAL: Show examples — GPT-3 (text only), GPT-4V (text + image), GPT-4o (text + image + audio).]**

**HOST (V.O.):**  
"Now in 2025 and 2026, we're in the era of truly multimodal models. Text, images, audio, video — all flowing through the same model, in a single conversation. And the three biggest players — OpenAI's GPT-4o, Google's Gemini 2.5 Pro, and Anthropic's Claude Opus 4.1 — they all claim to do this. But the way they do it? Wildly different."

**[VISUAL: Host on camera.]**

**HOST:**  
"Here's the key insight: multimodal doesn't just mean 'accepts multiple input types.' It means the model has a unified understanding across those types. When you show GPT-4o a photo of a whiteboard and ask it to explain the architecture, it's not running two separate systems — one for vision, one for language. It's one model that sees and reasons simultaneously."

**[VISUAL: Diagram showing unified vs. pipelined multimodal architecture.]**

**HOST (V.O.):**  
"That distinction matters because it affects everything — speed, accuracy, cost, and what you can actually build with it."

---

### [3:30–7:00] SEGMENT 2: GPT-4o — REAL-TIME NATIVE AUDIO

**[VISUAL: OpenAI branding. GPT-4o logo with audio waveform animation.]**

**HOST (V.O.):**  
"Let's start with GPT-4o, because OpenAI took the most radical approach to multimodality."

**[VISUAL: Technical diagram showing GPT-4o's native audio processing pipeline.]**

**HOST (V.O.):**  
"The 'o' in GPT-4o stands for 'omni.' And the big deal here is that GPT-4o processes audio natively. Not 'speech-to-text then text-to-speech' — that's what every other assistant was doing. GPT-4o hears your voice, understands tone, emotion, interruption, and responds directly in audio."

**[VISUAL: Show latency comparison — old pipeline ~2-3 seconds vs. GPT-4o ~320ms.]**

**HOST (V.O.):**  
"The average response time for voice mode is around 320 milliseconds. For context, a typical phone conversation has about 200 to 300 milliseconds of natural pause between turns. GPT-4o is operating within human conversational rhythm."

**[VISUAL: Host on camera.]**

**HOST:**  
"What this means practically is that you can interrupt GPT-4o mid-sentence and it handles it gracefully. It understands when you say 'wait, no, I meant...' and adjusts. That's not a small thing — that requires the model to be processing audio in real-time chunks, maintaining context, and being ready to pivot at any moment."

**[VISUAL: Show GPT-4o capabilities grid.]**

**HOST (V.O.):**  
"Here's the full capability breakdown for GPT-4o: text input and output, obviously. Image input — it can analyze photos, screenshots, diagrams, charts. Audio input and output — native, real-time. Video input — through the API, you can send video frames. And it can generate images through DALL-E 3 integration."

**[VISUAL: Show API pricing card for GPT-4o.]**

**HOST (V.O.):**  
"On pricing, GPT-4o comes in at $2.50 per million input tokens and $10.00 per million output tokens for text. Image inputs are priced by token count — a typical image runs about 1,000 tokens. Audio API is $100 per million input tokens and $200 per million output tokens. That audio pricing is steep, but remember, you're getting real-time native processing."

---

### [7:00–10:30] SEGMENT 3: GEMINI 2.5 PRO — THE CONTEXT KING

**[VISUAL: Google DeepMind branding. Gemini 2.5 Pro logo with a "2M" badge.]**

**HOST (V.O.):**  
"Now let's talk about Gemini 2.5 Pro, because Google went in a completely different direction."

**[VISUAL: Visual of a massive context window — show 2M tokens as a scroll unrolling.]**

**HOST (V.O.):**  
"Gemini 2.5 Pro's headline feature is its 2 million token context window. Let me put that in perspective: 2 million tokens is roughly 1.5 million words. That's about five copies of 'War and Peace.' In a single prompt."

**[VISUAL: Show use cases — entire codebases, long research papers, hours of video transcripts.]**

**HOST (V.O.):**  
"This means you can feed Gemini an entire codebase — every file, every test, every config — and ask it to find bugs, suggest refactors, or write documentation. You can upload hours of video and ask it to summarize specific moments. You can give it a 500-page legal contract and ask it to find every clause about liability."

**[VISUAL: Host on camera.]**

**HOST:**  
"But here's what's really interesting about Gemini's multimodal approach: Google built it from the ground up as a multimodal model. Unlike OpenAI, which started with text and added modalities over time, Gemini was designed to handle text, images, audio, and video from day one. The architecture is natively multimodal."

**[VISUAL: Architecture comparison — GPT-4o (added modalities) vs. Gemini (native multimodal).]**

**HOST (V.O.):**  
"Gemini 2.5 Pro handles text, images, audio, and video input. It can generate text and images. And with Google's ecosystem integration, it can pull from Google Search, YouTube, and other Google services for real-time information."

**[VISUAL: Show API pricing card for Gemini 2.5 Pro.]**

**HOST (V.O.):**  
"Pricing for Gemini 2.5 Pro: $1.25 per million input tokens for the first 200K tokens, then $2.50 per million beyond that. Output is $10.00 per million tokens. Image input is tokenized at about 1,000 tokens per image, similar to GPT-4o. Audio input is priced at $0.50 per million tokens — significantly cheaper than GPT-4o's audio pricing."

**[VISUAL: Host on camera.]**

**HOST:**  
"The catch? Gemini's audio processing isn't as real-time as GPT-4o's. It's more of a 'send audio file, get response' model rather than a true conversational voice experience. For most API use cases, that's fine. But if you're building a voice assistant, GPT-4o has the edge."

---

### [10:30–14:00] SEGMENT 4: CLAUDE OPUS 4.1 — THE REASONING ENGINE

**[VISUAL: Anthropic branding. Claude Opus 4.1 logo with a reasoning chain animation.]**

**HOST (V.O.):**  
"And then there's Claude Opus 4.1, which takes yet another approach to multimodality."

**[VISUAL: Show Claude's multi-step reasoning — a complex problem being broken into steps.]**

**HOST (V.O.):**  
"Claude's strength isn't raw speed or massive context — it's reasoning. When you give Claude a complex multimodal problem, it doesn't just answer it. It thinks through it step by step, and it's remarkably good at not making things up."

**[VISUAL: Host on camera.]**

**HOST:**  
"Here's what I mean. If you show all three models a complex diagram — say, a system architecture diagram with 20 components and ask them to identify potential failure points — Claude will methodically walk through each component, consider the dependencies, and give you a structured analysis. GPT-4o might be faster. Gemini might reference more external knowledge. But Claude's reasoning chain is the most thorough."

**[VISUAL: Show Claude's multimodal capabilities.]**

**HOST (V.O.):**  
"Claude Opus 4.1 handles text input and output, and image input. It can analyze photos, charts, graphs, screenshots, documents — and it's particularly good at extracting structured data from images. Think receipts, forms, tables, handwritten notes."

**[VISUAL: Show Claude's context window — 200K tokens.]**

**HOST (V.O.):**  
"Context window is 200,000 tokens — smaller than Gemini's 2 million, but still massive. That's about 150,000 words, or a few hundred pages of text. For most use cases, it's more than enough."

**[VISUAL: Show API pricing card for Claude Opus 4.1.]**

**HOST (V.O.):**  
"Pricing: $15.00 per million input tokens and $75.00 per million output tokens. Yes, you heard that right — Claude Opus 4.1 is significantly more expensive than both GPT-4o and Gemini. Image inputs are tokenized at roughly 1,000 to 1,500 tokens per image depending on resolution."

**[VISUAL: Host on camera.]**

**HOST:**  
"Now, before you write Claude off as too expensive — remember, you're paying for quality. In benchmarks, Claude Opus 4.1 consistently ranks at the top for reasoning, coding, and complex analysis. If you're building a chatbot that writes generic responses, use GPT-4o or Gemini. If you're building an AI that needs to think through hard problems, Claude is worth the premium."

---

### [14:00–14:30] TRANSITION

**[VISUAL: Animated transition — three logos orbiting, then lining up side by side.]**

**HOST (V.O.):**  
"So we've covered the theory. Now let's see them in action."

---

### [14:30–18:30] SEGMENT 5: LIVE DEMO — SAME PROMPT, THREE MODELS

**[VISUAL: Screen recording setup. Three terminal windows side by side, each labeled with the model name.]**

**HOST (V.O.):**  
"For this demo, I'm going to send the exact same multimodal prompt to all three models. The prompt is: 'Analyze this system architecture diagram and identify the top 3 scalability bottlenecks, then suggest specific improvements for each.'"

**[VISUAL: Show the image being sent — a system architecture diagram with load balancers, databases, caches, microservices, message queues.]**

**HOST (V.O.):**  
"I'm sending the same image to all three models via their APIs. Let's see what comes back."

**[VISUAL: Screen recording of API calls being made. Show the Python code briefly, then the responses appearing.]**

**HOST (V.O.):**  
"First up, GPT-4o. Response time: about 2.8 seconds. It identified the database as the primary bottleneck, the lack of caching layer, and the single message queue. Solid analysis, well-structured."

**[VISUAL: Show GPT-4o's response on screen.]**

**HOST (V.O.):**  
"Next, Gemini 2.5 Pro. Response time: about 3.5 seconds. It gave a more detailed analysis — it not only identified the same three bottlenecks but also referenced common patterns from large-scale systems. It mentioned specific technologies like Redis for caching and Kafka for message queuing."

**[VISUAL: Show Gemini's response on screen.]**

**HOST (V.O.):**  
"Finally, Claude Opus 4.1. Response time: about 5.2 seconds. But look at the quality. It didn't just identify bottlenecks — it walked through the data flow step by step, explained WHY each bottleneck matters, and prioritized them by impact. It also flagged a potential race condition in the service mesh that the other two missed."

**[VISUAL: Show Claude's response on screen.]**

**HOST (ON CAMERA):**  
"So what do we learn from this? GPT-4o is fast and solid. Gemini gives you breadth and external knowledge. Claude gives you depth and reasoning. Your choice depends on what you're building."

---

### [18:30–21:00] SEGMENT 6: COST COMPARISON

**[VISUAL: Animated comparison table building row by row.]**

**HOST (V.O.):**  
"Let's talk money, because at scale, the price differences matter a lot."

**[VISUAL: Show full pricing comparison table.]**

**HOST (V.O.):**  
"For text processing, GPT-4o costs $2.50 per million input tokens. Gemini 2.5 Pro is $1.25 for the first 200K, then $2.50. And Claude Opus 4.1 is $15.00 per million — six times more expensive than GPT-4o."

**[VISUAL: Show output pricing.]**

**HOST (V.O.):**  
"For output, GPT-4o is $10.00 per million tokens. Gemini is also $10.00. Claude is $75.00 — seven and a half times more than the others."

**[VISUAL: Show image pricing.]**

**HOST (V.O.):**  
"For images, all three charge by token count. A typical image is about 1,000 to 1,500 tokens. So for GPT-4o, each image costs about $0.0025 per image. Gemini is about $0.00125. Claude is about $0.015."

**[VISUAL: Show audio pricing.]**

**HOST (V.O.):**  
"Audio is where it gets interesting. GPT-4o charges $100 per million input tokens for audio — that's about $0.10 per minute of audio. Gemini charges $0.50 per million tokens — about $0.005 per minute. Claude doesn't have a native audio API."

**[VISUAL: Show monthly cost projection for a hypothetical app.]**

**HOST (V.O.):**  
"Let's say you're building an app that processes 10,000 multimodal requests per day. Each request has about 2,000 input tokens and 500 output tokens, plus one image. Here's your monthly cost:"

**[VISUAL: Show calculation.]**

- **GPT-4o:** ~$225/month
- **Gemini 2.5 Pro:** ~$187/month
- **Claude Opus 4.1:** ~$1,125/month

**HOST (ON CAMERA):**  
"Gemini is the cheapest for high-volume multimodal workloads. GPT-4o is competitive and gives you the best voice experience. Claude is premium — you use it when quality matters more than cost."

---

### [21:00–22:00] WRAP-UP & CTA

**[VISUAL: Host on camera. Clean background.]**

**HOST:**  
"So here's the bottom line. Multimodal AI isn't a feature — it's the foundation of everything we're building right now. And these three models represent three different philosophies."

**[VISUAL: Quick recap graphic.]**

**HOST (V.O.):**  
"GPT-4o is the all-rounder with the best real-time voice experience. Gemini 2.5 Pro is the context king with the best price-to-capability ratio. And Claude Opus 4.1 is the reasoning champion for when you need the highest quality output."

**[VISUAL: Host on camera.]**

**HOST:**  
"If this helped you understand multimodal AI, smash that like button and subscribe to On The FarSide Series. Drop a comment telling me which model you're using and why — I read every single one. Next episode, we're benchmarking all three on a real coding task, and the results might surprise you."

**[VISUAL: End screen with subscribe button, next episode preview, and social links. Orange accent glow.]**

**HOST (V.O.):**  
"See you on the FarSide."

**[VISUAL: Outro music. Channel logo animation.]**

---

## PRODUCTION NOTES

**Graphics needed:**
- Capability comparison table (3 columns x 6 rows)
- Pricing comparison table with per-token and per-image costs
- Monthly cost projection bar chart
- Architecture diagrams for each model's multimodal pipeline
- Live demo screen recording (3 terminal windows)

**Music:**
- High-energy intro (first 45 seconds)
- Neutral tech bed for explanation segments
- Slightly tense bed for comparison/competitive segments
- Upbeat outro

**B-roll:**
- API documentation screenshots
- Terminal recordings of actual API calls
- Architecture diagram images for the demo
- Token counting visualizations

**Code shown on screen:**
- `src/01_api_comparison.py` — pricing comparison
- `src/02_multimodal_demo.py` — multimodal API call structure
