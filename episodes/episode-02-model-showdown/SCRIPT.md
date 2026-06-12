# Episode 02 — Open Source AI Models Showdown: LLaMA vs Mistral vs Gemma vs Reka

**Series:** On The FarSide Series
**Book:** FarSide ChatGPT by NinjaTech AI Team, Joomo Enterprises Publishing
**Estimated Duration:** 15–20 minutes

---

## YouTube Description

```
Which open-source model should you actually use? I tested them all.

In this episode, we go head-to-head with the four biggest open-source AI models
of 2025: LLaMA 4 Scout, Mistral Medium 3.1, Gemma 3, and Reka Flash 3.1.
We break down real benchmark numbers, hardware requirements, licensing,
quantization trade-offs, and give you a clear decision framework so you can
pick the right model for YOUR use case.

TIMESTAMPS:
00:00 — Hook: The Open Source Model Dilemma
01:15 — The Contenders: Who Are These Models?
04:30 — Round 1: Benchmark Battle (MMLU, HumanEval, MATH, GSM8K)
08:00 — Round 2: Hardware Requirements & VRAM
10:45 — Round 3: Licensing — Can You Actually Use Them?
13:00 — Round 4: Quantization — Squeezing Models onto Your GPU
15:30 — Round 5: The Decision Framework
18:00 — Outro & Next Episode Preview

GITHUB: [link to repo]
BOOK: FarSide ChatGPT — available now

#OpenSourceAI #LLaMA #Mistral #Gemma #Reka #LLM #AI #FarSideChatGPT
```

---

## HOOK [00:00 – 01:15]

[ON CAMERA — Dark slate background, orange accent lighting]

"Which open-source model should you actually use? I tested them all."

[Cut to screen recording — terminal window]

"If you've spent any time in the AI space in 2025, you've seen the explosion.
LLaMA 4 Scout from Meta. Mistral Medium 3.1 from the French AI lab.
Gemma 3 from Google. Reka Flash 3.1 from the Singapore-based team.
Everyone claims theirs is the best. Everyone has a benchmark to prove it.
But which one should YOU actually run? On YOUR hardware? For YOUR project?"

[Cut back to camera]

"Today, we're settling this. Head to head. Four models. Five rounds.
Benchmarks. Hardware. Licensing. Quantization. And at the end, a decision
framework that tells you exactly which model to pick for your situation.
No fluff. No hype. Just data."

"Let's go."

---

## SECTION 1: THE CONTENDERS [01:15 – 04:30]

[ON CAMERA]

"Before we throw numbers around, let's meet the four models we're comparing."

### LLaMA 4 Scout — Meta

"First up: LLaMA 4 Scout from Meta. This is the latest in the LLaMA line,
and it's a mixture-of-experts model — meaning it only activates a fraction
of its parameters for any given token. Scout has 17B active parameters out of
a total of 109B. It supports a 10 million token context window, which is
absolutely massive. Meta released it under a custom license that's mostly
open but has some restrictions for companies with over 700 million monthly
active users."

### Mistral Medium 3.1 — Mistral AI

"Next: Mistral Medium 3.1 from Mistral AI, the French company that's been
punching way above its weight class. This is a dense model — all parameters
are active on every token. It's known for strong reasoning, excellent
instruction following, and it's released under the Apache 2.0 license, which
is about as permissive as it gets. Mistral has been a favorite in the
European AI community and is increasingly popular worldwide."

### Gemma 3 — Google

"Third: Gemma 3 from Google. This is Google's open-weight model family,
built on the same research that went into Gemini. Gemma 3 comes in multiple
sizes — 2B, 9B, and 27B — and it's released under a permissive license that
allows commercial use. Google has been pushing hard on the 'responsible AI'
angle with this one, and it shows in their safety evaluations."

### Reka Flash 3.1 — Reka AI

"And finally: Reka Flash 3.1 from Reka AI, a Singapore-based team founded by
researchers from Google, DeepMind, and Meta. Reka Flash is designed for
speed — it's optimized for fast inference on consumer hardware. It's a
multimodal model that handles both text and images, and it's released under
a custom license. Reka is the underdog in this fight, but don't count them out."

[Cut to screen — show model comparison table]

"Here's the quick spec overview. Let's put this on screen."

---

## SECTION 2: ROUND 1 — BENCHMARK BATTLE [04:30 – 08:00]

[SCREEN RECORDING — Run the benchmark script]

"Alright, Round 1. The numbers. Let's run our benchmark comparison script
and see how these models stack up."

[Run: python src/01_model_benchmarks.py]

"Let's walk through what we're seeing here."

### MMLU (Massive Multitask Language Understanding)

"MMLU tests knowledge across 57 subjects — everything from history to
computer science to law. It's the most widely cited benchmark in the field."

"LLaMA 4 Scout leads the pack here at 85.2. Mistral Medium 3.1 comes in
at 83.7. Gemma 3 sits at 82.1, and Reka Flash 3.1 at 81.5. The differences
are small — we're talking a few percentage points — but in the LLM world,
that can matter."

### HumanEval (Code Generation)

"HumanEval is a code generation benchmark. The model is given a function
description and has to write working Python code."

"Mistral takes this one at 78.3 percent. LLaMA is right behind at 76.8.
Gemma 3 hits 74.1, and Reka Flash at 72.6. If you're building a coding
assistant, Mistral has the edge here."

### MATH Dataset

"The MATH benchmark tests mathematical reasoning — competition-level math
problems. This is where things get interesting."

"LLaMA 4 Scout pulls ahead at 68.4 percent. Mistral is at 65.2. Gemma 3
at 63.8. Reka Flash at 61.1. The mixture-of-experts architecture seems to
help with complex reasoning tasks."

### GSM8K (Grade School Math)

"GSM8K is word problems at a middle school level. It tests whether the
model can set up and solve multi-step problems."

"All four models score above 90 here — LLaMA at 95.1, Mistral at 94.3,
Gemma 3 at 93.7, Reka Flash at 92.8. At this level, they're all competent.
The differences won't matter for most applications."

### Overall Takeaway

"So what's the verdict? LLaMA 4 Scout wins the most benchmarks overall,
especially on knowledge and reasoning. Mistral dominates on code generation.
Gemma 3 is consistently strong across the board — no weaknesses, no standout
wins. Reka Flash trails slightly but remember: it's optimized for speed,
not benchmark scores."

"Benchmarks aren't everything, though. Let's talk about what it actually
takes to run these models."

---

## SECTION 3: ROUND 2 — HARDWARE REQUIREMENTS & VRAM [08:00 – 10:45]

[SCREEN RECORDING — Run the hardware requirements script]

"Round 2: Can you actually run these models on YOUR hardware? Let's check
our hardware requirements script."

[Run: python src/02_hardware_requirements.py]

"Here's the reality check. Running these models locally requires VRAM —
lots of it, depending on the model size and quantization level."

### FP16 (Full Precision)

"At full FP16 precision — the gold standard for quality — a 7B model
needs about 14 gigabytes of VRAM. A 13B model needs 26 gig. And a 70B
model? 140 gigabytes. That's multiple data center GPUs."

"Nobody's running 70B at FP16 on a consumer card. Let's be real."

### 8-bit Quantization

"8-bit quantization cuts those requirements roughly in half. Now your 7B
model fits in 8 gigabytes — doable on an RTX 3070 or 4060 Ti 16GB.
A 13B model needs about 14 gigabytes — an RTX 3080 or 4070. A 70B model
still needs 74 gigabytes, which means dual 4090s or a single A6000."

### 4-bit Quantization (GGUF)

"This is where it gets interesting for most people. 4-bit quantization —
using the GGUF format through llama.cpp or Ollama — brings a 7B model
down to about 4 gigabytes. That runs on almost anything. A laptop with
16 gigabytes of unified memory? You're running a 13B model. A 70B model
at 4-bit needs about 38 gigabytes — a single RTX 6000 Ada or a Mac Studio
with 64 gigabytes of unified memory."

### CPU + RAM (No GPU)

"And if you don't have a GPU at all? You can run these on CPU, but it's
slow. A 7B model at 4-bit on a modern CPU with 16 gigabytes of RAM will
give you maybe 5 to 10 tokens per second. Usable for testing, but not
for production."

[Cut back to camera]

"The takeaway: if you have a modern GPU with 8 to 12 gigabytes of VRAM,
you can comfortably run 7B to 13B models at 4-bit. If you have 24 gig or
more, you can push to 70B at 4-bit. Know your hardware, pick your model
size accordingly."

---

## SECTION 4: ROUND 3 — LICENSING [10:45 – 13:00]

[ON CAMERA]

"Round 3 is one that a lot of people overlook, but it matters — especially
if you're building a product. Let's talk licensing."

### LLaMA 4 Scout — Custom Meta License

"LLaMA 4 uses Meta's custom license. It's open-source in the sense that
you can download and use the weights, but there's a catch: if your product
has more than 700 million monthly active users, you need a separate license
from Meta. For 99.9 percent of developers, this is irrelevant. But if
you're building the next big app, it's something to be aware of."

### Mistral Medium 3.1 — Apache 2.0

"Mistral uses Apache 2.0. This is the gold standard for permissive licensing.
You can use it commercially, modify it, distribute it, sublicense it.
The only requirement is that you include the original copyright notice
and license text. No restrictions on user count. No restrictions on use case.
If you want zero legal headaches, Mistral is your friend."

### Gemma 3 — Google Permissive License

"Gemma 3 uses Google's own permissive license. It allows commercial use,
modification, and distribution. Google has committed to keeping it open,
and there are no user-count restrictions. The license does include some
use-of-branding restrictions — you can't imply Google endorses your product
— but that's standard stuff."

### Reka Flash 3.1 — Custom License

"Reka uses a custom license that allows research and commercial use but
has some restrictions on redistribution of modified weights. It's more
permissive than Meta's license but less permissive than Apache 2.0.
If you're building something that involves sharing modified models, read
the fine print."

### Licensing Verdict

"For most developers: Mistral and Gemma 3 are the safest choices. Apache 2.0
and Google's license give you maximum flexibility. LLaMA is fine unless
you're building at massive scale. Reka is good but check the redistribution
terms if that's part of your workflow."

---

## SECTION 5: ROUND 4 — QUANTIZATION DEEP DIVE [13:00 – 15:30]

[SCREEN RECORDING]

"Round 4: Quantization. This is the magic that makes running large models
on consumer hardware possible. Let's break it down."

### What Is Quantization?

"Quantization reduces the precision of the model's weights. Instead of
storing each weight as a 16-bit floating point number, you store it as
8-bit, 4-bit, or even 2-bit integers. The model gets smaller, runs faster,
but loses a tiny bit of quality."

### The Trade-offs

"The key question is: how much quality do you lose? In practice, 8-bit
quantization is virtually lossless — you won't notice the difference.
4-bit is where most people land. The quality drop is minimal for most
tasks — maybe 1 to 2 percent on benchmarks. For chat, coding, and general
use, it's imperceptible."

"2-bit and 3-bit are more aggressive. You'll see quality degradation on
complex reasoning tasks, but for simple chat and classification, they can
still work."

### GGUF Format

"The GGUF format — developed by the llama.cpp team — is the most popular
way to run quantized models. It supports quantization levels from 2-bit
to 8-bit, and it's compatible with tools like Ollama, LM Studio, and
text-generation-webui."

"If you're running models locally, you're almost certainly using GGUF.
It's the de facto standard."

### Recommended Quantization Levels

"Here's my recommendation: for 7B models, use Q4_K_M — it's the sweet
spot between size and quality. For 13B models, same thing — Q4_K_M.
For 70B models, if you have the VRAM, go Q4_K_M. If you're tight on
memory, Q3_K_M is acceptable."

---

## SECTION 6: ROUND 5 — THE DECISION FRAMEWORK [15:30 – 18:00]

[ON CAMERA — Show decision flowchart on screen]

"Alright, the final round. You've seen the benchmarks, the hardware
requirements, the licensing, and the quantization trade-offs. Now let me
give you a simple decision framework."

### Scenario 1: "I want the best overall model"

"Go with LLaMA 4 Scout. It wins the most benchmarks, has the largest
context window, and the mixture-of-experts architecture is efficient.
The only caveat is the licensing — make sure the 700 million user
restriction doesn't apply to you."

### Scenario 2: "I'm building a coding assistant"

"Mistral Medium 3.1. It leads on HumanEval, has Apache 2.0 licensing,
and its dense architecture means consistent performance. If you're building
a code generation tool, Mistral is the way to go."

### Scenario 3: "I want maximum legal freedom"

"Mistral Medium 3.1 or Gemma 3. Both have fully permissive licenses
with no user-count restrictions. You can build whatever you want,
sell it to whoever you want, and never worry about licensing issues."

### Scenario 4: "I'm on a budget — consumer hardware"

"Run a 7B or 13B model at 4-bit quantization. Gemma 3 9B at Q4_K_M
is an excellent choice — it runs on a single RTX 3070, has a permissive
license, and performs well across the board. If you have more VRAM,
LLaMA 4 Scout at 4-bit is the best quality you can get."

### Scenario 5: "I need speed above all else"

"Reka Flash 3.1. It's designed for fast inference. The benchmark scores
are slightly lower, but the tokens-per-second on consumer hardware is
excellent. If you're building a real-time chat application where latency
matters more than perfect accuracy, Reka is your pick."

### Scenario 6: "I need multimodal — text and images"

"Both Gemma 3 and Reka Flash 3.1 support multimodal inputs. Gemma 3 has
better image understanding benchmarks, but Reka Flash is faster. Pick
based on whether you prioritize quality or speed."

[Cut back to camera]

"There you have it. Six scenarios, six clear answers. The 'best' model
depends entirely on YOUR use case. That's the whole point of this episode."

---

## OUTRO [18:00 – 20:00]

[ON CAMERA]

"So — which open-source model should you actually use? Now you know.
It depends on your hardware, your use case, your licensing needs,
and your priorities."

"Here's the quick cheat sheet:"

[Show on screen:]
```
BEST OVERALL:        LLaMA 4 Scout
BEST FOR CODING:     Mistral Medium 3.1
BEST LICENSING:      Mistral Medium 3.1 / Gemma 3
BEST ON BUDGET HW:   Gemma 3 9B (Q4_K_M)
BEST FOR SPEED:      Reka Flash 3.1
BEST MULTIMODAL:     Gemma 3
```

"If this episode helped you, smash that like button. Subscribe to the
channel. And if you want to go deeper on this topic, check out the book —
'FarSide ChatGPT' by the NinjaTech AI Team, published by Joomo Enterprises.
It covers everything we talked about today and way more."

"Next episode, we're going hands-on: we'll set up a local inference server
with Ollama, load up these models, and test them in real time. You won't
want to miss it."

"Until then — stay on the FarSide."

[END CARD — Orange on dark slate, subscribe button, next episode link]

---

## Production Notes

- **B-Roll Needed:** Terminal recordings of both Python scripts running,
  GPU monitoring (nvidia-smi), model download progress
- **Graphics:** Comparison table animations, benchmark bar charts,
  decision flowchart, hardware requirement table
- **Music:** Upbeat electronic intro, ambient background during explanations
- **Thumbnail:** Split screen showing 4 model logos with VS text overlay
  and "I TESTED THEM ALL" in orange bold text
- **Color Scheme:** Dark slate (#1a1a2e) background, Orange (#ff6b35)
  accents, White (#ffffff) text
