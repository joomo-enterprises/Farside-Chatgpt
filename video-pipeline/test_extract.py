import sys
sys.path.insert(0, "scripts")
from slidemaker import extract_narration_points

narr = 'But here is the thing about free tools from big companies - you are not the customer. PROBLEM 1: Vendor Lock-in. Every app you build on GPT-4 lives and dies by OpenAI API. PROBLEM 2: Data Privacy. Everything you send to ChatGPT goes through their servers. PROBLEM 3: Cost at Scale. Say your app makes 1000 calls per day. That is roughly 30-90 per day.'

r = extract_narration_points(nar)
print("points:", len(r["points"]))
for p in r["points"]:
    print(" -", p[:80])
print("takeaway:", r["takeaway"])
print("sections:", len(r["sections"]))
if "The tr" in r["takeaway"]:
    print("BAD: truncation detected")
else:
    print("OK: no truncation")
