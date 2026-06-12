# Episode 6: AI Ethics You Cannot Ignore — Bias, Privacy, and the Future of Work

**Series:** On The FarSide  
**Duration:** ~16 minutes  
**Format:** Talking Head + Case Study + Live Code Demo

---

## FULL VIDEO SCRIPT

---

### [00:00–00:45] COLD OPEN — HOOK

**[TALKING HEAD — DIRECT TO CAMERA. SERIOUS TONE.]**

> "Before you ship that AI app, you need to watch this."

**[BEAT — 1 second of silence.]**

> "Not because I'm going to tell you AI is dangerous. Not because you should stop building. But because the decisions you make *right now* — about your data, your models, your users — those decisions are going to define whether your AI product helps people… or quietly harms them."

> "I've been building AI systems for years. And I can tell you: nobody gave me a manual for the ethics side. No one sat me down and said, 'Hey, here's how you check if your model is discriminating against people.' I had to learn it the hard way."

> "Today, we're fixing that. We're going to cover bias in training data, fairness metrics you can actually compute, GDPR compliance, model auditing, the future of work, and — most importantly — how to build ethical AI from day one."

> "Let's go."

**[TITLE CARD: "AI Ethics You Cannot Ignore — Bias, Privacy, and the Future of Work"]**

---

### [00:45–03:30] SEGMENT 1 — BIAS IN TRAINING DATA

**[TALKING HEAD]**

> "Let's start with the biggest, most common, most *ignored* problem: bias in training data."

> "Your model is a mirror. It reflects the data you feed it. And if that data is biased — and it almost always is — your model will be biased too."

**[CASE STUDY ON SCREEN — TEXT OVERLAY]**

> "In 2018, Amazon scrapped an AI recruiting tool after discovering it was systematically downgrading resumes that contained the word 'women's' — as in 'women's chess club' or 'women's studies.' The model was trained on ten years of hiring decisions, and those decisions were made in a male-dominated industry. So the model learned: 'men are better candidates.'"

> "That's not a bug in the algorithm. That's a bug in the data. And it cost Amazon millions."

**[TALKING HEAD]**

> "Here's what you need to understand. Bias doesn't look like slurs in your dataset. Bias looks like *imbalance*. It looks like underrepresentation. It looks like historical patterns of discrimination encoded as 'ground truth.'"

> "Let me show you a quick example."

**[SCREEN RECORDING — LIVE CODE]**

```python
# Quick demonstration: checking for dataset imbalance
dataset = {
    "loan_applicants": {
        "male": 8500,
        "female": 3200,
        "non_binary": 150
    },
    "approved": {
        "male": 6800,
        "female": 2100,
        "non_binary": 80
    }
}
```

> "Look at this. We have 8,500 male loan applicants, 3,200 female, and 150 non-binary. Immediately, you can see the dataset skews heavily male. But here's the kicker — look at the approval rates."

> "Males: 80%. Females: about 65%. Non-binary: 53%. The model trained on *this* data is going to learn that gender correlates with creditworthiness. That's not just wrong — it's illegal in many jurisdictions."

**[TALKING HEAD]**

> "So what do you do? Step one: always profile your training data before you train anything. We're going to write a script for that right after this segment. Step two: ask who's missing from your dataset. Step three: be suspicious of your ground truth — historical decisions are often tainted with human bias."

---

### [03:30–05:00] CODE DEMO 1 — BIAS DETECTOR

**[SCREEN RECORDING — TERMINAL]**

> "Alright, let's write a bias detector. I want you to run this on every dataset before you train anything."

**[LIVE CODING — `src/01_bias_detector.py`]**

```python
python src/01_bias_detector.py
```

**[SHOW OUTPUT]**

```
=== BIAS DETECTION REPORT ===
Dataset: sample_hiring_data
Total samples: 11,850

=== Demographic Distribution ===
Group        Count    Percentage
-------------------------------
male          8,500      71.7%
female        3,200      27.0%
non_binary      150       1.3%

⚠️  IMBALANCE DETECTED: Male representation (71.7%) exceeds 3x average
⚠️  UNDERREPRESENTED: non_binary (1.3% — below 5% threshold)
⚠️  POTENTIAL BIAS RISK: HIGH

Recommendation: Collect more data for underrepresented groups before training.
Recommendation: Apply resampling or weighting strategies to balance classes.
```

> "See that? In thirty lines of code, you've caught a bias problem that could have cost you millions and harmed real people. This is non-negotiable. Run this. Every time."

---

### [05:00–08:30] SEGMENT 2 — FAIRNESS METRICS

**[TALKING HEAD]**

> "Okay, so you've cleaned your data. You've profiled it. You've caught the obvious imbalances. But bias can still hide in your model's *predictions*. That's why we need fairness metrics."

> "Fairness metrics are mathematical definitions of what 'fair' means in your specific context. And here's the uncomfortable truth: they're often *mutually exclusive*. You can't always satisfy all of them at once. You have to choose which one matters most for your use case."

**[WHITEBOARD / ANIMATED DIAGRAM ON SCREEN]**

> "Let's talk about the big three."

**Demographic Parity:**

> "A model satisfies demographic parities if the probability of a positive outcome is the same across all demographic groups. In other words: if 70% of men get approved, then 70% of women should get approved too. Simple. Clean. But it ignores a critical question — what if the underlying qualifications *actually differ*? That's where it gets murky."

**Equalized Odds:**

> "Equalized odds is stricter. It says: the model's *error rates* should be equal across groups. So the false positive rate — people wrongly approved — and the false negative rate — people wrongly rejected — should be the same for men and women and every other group. This accounts for actual differences in the ground truth while ensuring the model doesn't make *disproportionate* errors for any group."

**Predictive Parity:**

> "Predictive parity says: when the model predicts 'yes,' how often is it right? That accuracy should be consistent across groups. If my model says 'this person will repay the loan,' that prediction should be equally reliable whether the person is male or female."

**[TALKING HEAD]**

> "The 2016 ProPublica analysis of the COMPAS recidivism algorithm found that the tool had equal predictive parity across races… but wildly different false positive rates. Black defendants were nearly twice as likely as white defendants to be falsely flagged as high-risk. Same predictive parity. Very different real-world harm."

> "Which metric you choose matters. It's a *policy decision*, not just a technical one."

---

### [08:30–10:00] CODE DEMO 2 — FAIRNESS METRICS

**[SCREEN RECORDING — TERMINAL]**

> "Let's compute these three metrics with a real mock dataset. Run the script."

**[LIVE CODING — `src/02_fairness_metrics.py`]**

```python
python src/02_fairness_metrics.py
```

**[SHOW OUTPUT]**

```
=== FAIRNESS METRICS ANALYSIS ===
Mock Data: Hiring Decisions by Gender

--- Demographic Parity ---
P(Approved | male)   = 0.735
P(Approved | female) = 0.635
P(Approved | other)  = 0.600

Demographic Parity Difference: 0.135
⚠️  Threshold exceeded (>0.1) — Demographic parity NOT satisfied

--- Equalized Odds ---
                 FPR     FNR
Group male:    0.150   0.200
Group female:  0.220   0.280
Group other:   0.250   0.300

Max FPR difference: 0.100
Max FNR difference: 0.100
⚠️  Both exceed 0.05 threshold — Equalized odds NOT satisfied

--- Predictive Parity ---
PPV (precision) by group:
  male:   0.82
  female: 0.74
  other:  0.71

Predictive Parity Difference: 0.11
⚠️  Threshold exceeded (>0.1) — Predictive parity NOT satisfied

=== VERDICT: Model FAILS all three fairness metrics ===
Recommendation: Review training data, apply fairness constraints,
                and re-evaluated after mitigation.
```

> "This is what a red flag looks like. All three metrics fail. This model is not fair by any standard definition. And if this were a real hiring tool, you'd need to go back to the drawing board before deploying."

---

### [10:00–11:30] SEGMENT 3 — LIME / SHAP EXPLAINABILITY

**[TALKING HEAD]**

> "Now, here's a question every AI builder should be able to answer: *why did my model make that prediction?* If you can't answer that, you can't debug it, you can't audit it, and you can't defend it."

> "Two tools dominate this space: LIME and SHAP."

**[SCREEN — DIAGRAM COMPARING LIME AND SHAP]**

> "LIME — Local Interpretable Model-agnostic Explanations — works by tweaking individual predictions slightly and seeing how the output changes. It gives you a local, human-readable explanation for a single prediction. 'The model rejected this loan because income was below $30K and credit score was below 650.'"

> "SHAP — SHapley Additive exPlanations — is rooted in game theory. It computes each feature's *contribution* to the final prediction, averaged across all possible feature combinations. It's more theoretically grounded but computationally heavier."

> "For most practical purposes, SHAP gives you better global insights — you can see which features drive predictions across your *entire* dataset. LIME is faster and better for single-instance explanations."

> "My recommendation? Use SHAP for model development and auditing. Use LIME for customer-facing explanations — 'Here's why your application was decided this way.'"

**[TALKING HEAD]**

> "And remember: if your model's top features include race, gender, or zip code — which is often a proxy for race — you have a problem. Explainability tools help you catch it."

---

### [11:30–13:30] SEGMENT 4 — GDPR COMPLIANCE & MODEL AUDITING

**[TALKING HEAD]**

> "Let's talk about the law. Specifically, the GDPR — the General Data Protection Regulation. It applies if you have users in the EU, and honestly, it's become a de facto global standard."

> "Article 22 is the big one for AI: users have the right *not* to be subject to decisions made solely by automated systems. If your AI is rejecting loan applications, screening resumes, or predicting criminal risk, your users have a right to an explanation and a right to a human review."

**[SCREEN — CHECKLIST]**

> "Here's your GDPR compliance checklist for AI systems:"

> "One — Data Minimization. Only collect what you need. If your loan model doesn't need race data, don't collect it."

> "Two — Right to Explanation. Be ready to explain any automated decision in plain language."

> "Three — Right to Erasure. If a user asks you to delete their data, you must comply — including removing its influence from trained models. That last part is hard. Look into *machine unlearning* techniques."

> "Four — Data Protection Impact Assessment. Before deploying an AI system that processes personal data at scale, you must assess the risks."

> "Five — Consent and Purpose Limitation. You can't collect data for one purpose and quietly use it for another."

**[TALKING HEAD]**

> "Now, model auditing. This isn't optional anymore. The EU AI Act, signed in 2024, classifies AI systems by risk level. High-risk AI — used in hiring, lending, healthcare, criminal justice — must undergo conformity assessments, maintain audit trails, and demonstrate ongoing monitoring."

> "Build your audit infrastructure now. Log every prediction. Track model versions. Record training data snapshots. When an auditor asks, 'Why did this system behave this way on March 14th?' — you should be able to point to an answer."

---

### [13:30–15:30] SEGMENT 5 — JOB DISPLACEMENT VS AUGMENTATION

**[TALKING HEAD]**

> "Okay, let's tackle the question everyone's asking: is AI going to take our jobs?"

**[SCREEN — SPLIT HISTORY / FUTURE GRAPHIC]**

> "Let me give you the honest answer: yes and no."

> "Goldman Sachs estimated that generative AI could expose 300 million full-sized jobs to automation. Let that number sink in."

> "But here's the nuance. Most jobs aren't a single task — they're a collection of tasks. AI isn't automating *jobs*. It's automating *tasks*."

> "Radiologists, for example. AI can now read certain scans as well as humans. Does that mean radiologists are gone? No. It means radiologists who use AI will be more productive — they'll catch more, faster. The job changes. It doesn't disappear."

**[CASE STUDY]**

> "Look at what happened at Moody's. They didn't fire their financial analysts when they deployed GPT-powered tools. They gave every analyst an AI assistant. Productivity went up 30%. Headcount stayed the same. But the *work* changed — less time on routine analysis, more time on judgment-intensive decisions."

> "The displacement happens when you have a job that is — entirely — a collection of automatable tasks. Data entry. Basic customer service. Simple document review. Those roles are genuinely at risk."

**[TALKING HEAD]**

> "So what should you do? If you're building AI, build *with* humans in the loop. If you're a professional, learn to use AI tools. The future belongs to people who *collaborate* with AI, not people who compete with it."

> "And if you're a leader making deployment decisions — please, think about the human impact. Don't just automate for efficiency gains. Redesign the work *with* your people."

---

### [15:30–16:30] SEGMENT 6 — BUILDING ETHICAL AI: A PRACTICAL FRAMEWORK

**[TALKING HEAD]**

> "Let me leave you with a practical framework. This is what I use on every project."

**[SCREEN — FRAMEWORK SLIDE]**

> "**The Five Pillars of Ethical AI:**"

> "**1. Data Integrity.** Profile your data before training. Catch imbalance early. Run the bias detector. Document your data lineage. Know where every byte came from."

> "**2. Fairness by Design.** Choose your fairness metric *before* you train. Define it explicitly. Test for it rigorously. Don't wait for a lawsuit to discover bias."

> "**3. Explainability.** Use SHAP or LIME. Be able to explain any prediction. If you can't explain it, don't deploy it."

> "**4. Compliance.** Know the regulations. GDPR. EU AI Act. Sector-specific rules. They're not going away — they're expanding."

> "**5. Human Oversight.** Never deploy autonomous AI for high-stakes decisions without a human in the loop. Always."

**[TALKING HEAD]**

> "This isn't about being 'woke' or avoiding controversy. This is about building products that are *legally defensible*, *socially responsible*, and ultimately *more robust*. Fair models generalize better. Compliant products access more markets. Ethical AI is good engineering."

---

### [16:30–17:00] CLOSE

**[TALKING HEAD — DIRECT TO CAMERA]**

> "AI is the most powerful tool we've built in a generation. The question isn't whether we'll use it — we will. The question is: will we use it *wisely*?"

> "Bias isn't a bug you patch. Privacy isn't a footnote. The future of work isn't something that just *happens to us* — we shape it with every design decision we make."

> "So before you ship that AI app — audit your data, test your metrics, check your compliance, and put humans in the loop."

> "That's what separates good AI engineers from great ones."

> "I'll see you in Episode 7."

**[END CARD — SUBSCRIBE / NEXT EPISODE PREVIEW]**

---

## TIMESTAMES SUMMARY

| Timestamp   | Segment                                                    |
|-------------|------------------------------------------------------------|
| 00:00–00:45 | Cold Open / Hook                                           |
| 00:45–03:30 | Segment 1: Bias in Training Data (w/ Amazon case study)    |
| 03:30–05:00 | Code Demo 1: Bias Detector (`01_bias_detector.py`)         |
| 05:00–08:30 | Segment 2: Fairness Metrics (w/ COMPAS case study)         |
| 08:30–10:00 | Code Demo 2: Fairness Metrics (`02_fairness_metrics.py`)   |
| 10:00–11:30 | Segment 3: LIME / SHAP Explainability                      |
| 11:30–13:30 | Segment 4: GDPR Compliance & Model Auditing                |
| 13:30–15:30 | Segment 5: Job Displacement vs Augmentation                |
| 15:30–16:30 | Segment 6: Building Ethical AI — Five Pillars Framework    |
| 16:30–17:00 | Closing                                                    |

---

## PRODUCTION NOTES

- **Tone:** Serious but not preachy. Authoritative. Practical.
- **Graphics needed:** Framework slide (Five Pillars), GDPR checklist, LIME vs SHAP comparison, Timeline graphic for job automation stats.
- **Music:** Minimal. Ambient underscoring in case study segments. No music during talking head segments.
- **B-roll:** Stock footage of data centers, office environments, diverse team meetings, code on screens.
- **Casualties:** Amazon recruiting AI, COMPAS algorithm, Moody's AI deployment.
- **Scripts:** Two code demos. Test all scripts before recording. Expected outputs noted in each segment.
- **Deliverables:** SCRIPT.md, `src/01_bias_detector.py`, `src/02_fairness_metrics.py`
