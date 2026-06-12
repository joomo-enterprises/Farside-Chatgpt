"""
Episode 7 — Bayes Theorem Calculator for AI Scenarios
=====================================================
Interactive Bayes theorem calculator with pre-built AI/ML scenarios.

Bayes Theorem:  P(A|B) = P(B|A) * P(A) / P(B)

Standard library only — no NumPy, no SciPy.
"""

import sys


# =============================================================================
# CORE BAYES THEOREM
# =============================================================================

def bayes_theorem(prior, likelihood, evidence):
    """Apply Bayes theorem.
    
    P(A|B) = P(B|A) * P(A) / P(B)
    
    Parameters:
        prior:      P(A)  — how likely A is before seeing evidence
        likelihood: P(B|A)  — how likely we see evidence B if A is true
        evidence:   P(B)  — total probability of seeing evidence B
    
    Returns:
        posterior:  P(A|B) — updated probability of A given evidence B
    """
    if evidence == 0:
        return 0.0
    return (likelihood * prior) / evidence


def total_probability(likelihood_if_true, prior_true, likelihood_if_false, prior_false):
    """Compute total probability: P(B) = P(B|A)*P(A) + P(B|not_A)*P(not_A)
    
    This combines both scenarios: evidence appearing when A is true,
    AND evidence appearing when A is false.
    """
    return likelihood_if_true * prior_true + likelihood_if_false * prior_false


def update_belief(prior, likelihood_true, likelihood_false):
    """One-step Bayes update combining total probability and posterior.
    
    Given:
        prior:            P(A)
        likelihood_true:  P(B|A)
        likelihood_false: P(B|not_A)
    
    Returns:
        posterior: P(A|B)
    """
    p_not_a = 1.0 - prior
    p_b = total_probability(likelihood_true, prior, likelihood_false, p_not_a)
    return bayes_theorem(prior, likelihood_true, p_b)


def sequential_update(prior, evidence_list):
    """Update belief sequentially as multiple pieces of evidence arrive.
    
    This is how real AI systems work — each new piece of data
    shifts the probability a bit more.
    
    Parameters:
        prior:        Starting probability P(A)
        evidence_list: List of (P(B|A), P(B|not_A)) tuples
    
    Returns:
        List of posterior probabilities after each piece of evidence
    """
    current = prior
    posteriors = [current]
    
    for likelihood_true, likelihood_false in evidence_list:
        current = update_belief(current, likelihood_true, likelihood_false)
        posteriors.append(current)
    
    return posteriors


# =============================================================================
# PRE-BUILT AI SCENARIOS
# =============================================================================

def scenario_spam_detection():
    """Bayesian spam filter."""
    print("=" * 65)
    print("  SCENARIO 1: SPAM DETECTION")
    print("=" * 65)
    print()
    print("  Problem: An email contains the word 'free'. Is it spam?")
    print("  We use Bayes theorem to combine multiple words as evidence.")
    print()
    
    # Base rates
    p_spam = 0.20  # 20% of emails are spam
    
    # Word probabilities in spam vs ham
    words = {
        "free":    (0.30, 0.03),   # (P(word|spam), P(word|ham))
        "money":   (0.25, 0.02),
        "winner":  (0.20, 0.01),
        "meeting": (0.05, 0.25),
        "project": (0.03, 0.30),
    }
    
    print("  Base rate:  P(spam) = 20%")
    print("  Word likelihoods:")
    print(f"    {'Word':<12s} {'P(word|spam)':>14s} {'P(word|ham)':>14s}")
    print(f"    {'─'*12}  {'─'*14}  {'─'*14}")
    for word, (p_ws, p_wh) in words.items():
        print(f"    {word:<12s} {p_ws:>14.3f} {p_wh:>14.3f}")
    
    # Scenario A: Email has 'free'
    print("\n  --- Email A: contains 'free' ---")
    posterior = update_belief(p_spam, words["free"][0], words["free"][1])
    print(f"    P(spam|'free') = {posterior:.4f} = {posterior*100:.1f}%")
    
    # Scenario B: Email has 'free' AND 'money'
    print("\n  --- Email B: contains 'free' and 'money' ---")
    evidence_seq = [words["free"], words["money"]]
    posteriors = sequential_update(p_spam, evidence_seq)
    print(f"    After 'free':    P(spam) = {posteriors[1]:.4f} ({posteriors[1]*100:.1f}%)")
    print(f"    After 'money':   P(spam) = {posteriors[2]:.4f} ({posteriors[2]*100:.1f}%)")
    
    # Scenario C: Email has 'free' AND 'project' (mixed signals)
    print("\n  --- Email C: contains 'free' AND 'project' ---")
    evidence_seq = [words["free"], words["project"]]
    posteriors = sequential_update(p_spam, evidence_seq)
    print(f"    After 'free':     P(spam) = {posteriors[1]:.4f} ({posteriors[1]*100:.1f}%)")
    print(f"    After 'project':  P(spam) = {posteriors[2]:.4f} ({posteriors[2]*100:.1f}%)")
    print(f"    -> 'project' pulled the probability back down! Mixed evidence.")
    
    # Heat map: what if evidence gets stronger?
    print("\n  --- Sensitivity: As P('free'|spam) increases ---")
    print(f"    {'P(free|spam)':>14s}  {'P(spam|free)':>14s}  {'verdict':>12s}")
    print(f"    {'─'*14}  {'─'*14}  {'─'*12}")
    for p_free_spam in [0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90]:
        post = update_belief(p_spam, p_free_spam, words["free"][1])
        verdict = "LIKELY SPAM" if post > 0.5 else "PROBABLY HAM"
        print(f"    {p_free_spam:>14.2f}  {post:>14.4f}  {verdict:>12s}")


def scenario_medical_diagnosis():
    """Bayesian medical diagnosis."""
    print("\n\n" + "=" * 65)
    print("  SCENARIO 2: MEDICAL DIAGNOSIS")
    print("=" * 65)
    print()
    print("  Problem: A patient tests positive for a disease.")
    print("  How likely are they to ACTUALLY have it?")
    print("  (This is where most people — including doctors — get it wrong.)")
    print()
    
    # Disease: affects 1 in 1000 people
    p_disease = 0.001
    
    # Test accuracy
    p_positive_if_disease = 0.99   # Sensitivity (true positive rate)
    p_positive_if_healthy = 0.05   # False positive rate
    
    print(f"  Base rate:      P(disease) = {p_disease} (1 in 1000)")
    print(f"  Test sensitivity: P(+|disease) = {p_positive_if_disease} (99%)")
    print(f"  False positive:   P(+|healthy) = {p_positive_if_healthy} (5%)")
    print()
    
    posterior = update_belief(p_disease, p_positive_if_disease, p_positive_if_healthy)
    
    print(f"  BAYES CALCULATION:")
    print(f"    P(disease|+) = P(+|disease) * P(disease) / P(+)")
    print(f"    P(+) = P(+|disease)*P(disease) + P(+|healthy)*P(healthy)")
    print(f"         = {p_positive_if_disease}*{p_disease} + {p_positive_if_healthy}*{1-p_disease}")
    print(f"         = {p_positive_if_disease * p_disease:.5f} + {p_positive_if_healthy * (1-p_disease):.5f}")
    print(f"         = {total_probability(p_positive_if_disease, p_disease, p_positive_if_healthy, 1-p_disease):.5f}")
    print(f"    P(disease|+) = {p_positive_if_disease}*{p_disease} / {total_probability(p_positive_if_disease, p_disease, p_positive_if_healthy, 1-p_disease):.5f}")
    print(f"                = {posterior:.4f}")
    print()
    print(f"  RESULT: P(disease|positive test) = {posterior*100:.2f}%")
    print(f"  ---")
    print(f"  WAIT, WHAT?! A 99% accurate test, and only a {posterior*100:.2f}% chance")
    print(f"  of actually having the disease?!")
    print()
    print(f"  YES. This is the BASE RATE FALLACY.")
    print(f"  Because the disease is rare (1 in 1000), even a good test")
    print(f"  generates far more FALSE POSITIVES than TRUE POSITIVES.")
    print()
    print(f"  Out of 100,000 people tested:")
    print(f"    Have disease AND test positive: {int(100000 * p_disease * p_positive_if_disease)} (true positives)")
    print(f"    Healthy   AND test positive:    {int(100000 * (1-p_disease) * p_positive_if_healthy)} (false positives!)")
    print(f"    So {int(100000 * p_disease * p_positive_if_disease)} / {int(100000 * p_disease * p_positive_if_disease + 100000 * (1-p_disease) * p_positive_if_healthy)} = {posterior*100:.1f}% of positives are real.")
    
    # What about a SECOND test?
    print(f"\n  --- What if we run a SECOND test (also positive)? ---")
    posterior2 = update_belief(posterior, p_positive_if_disease, p_positive_if_healthy)
    print(f"    P(disease|++ ) = {posterior2:.4f} = {posterior2*100:.2f}%")
    print(f"    Two positive tests: much more confident!")
    
    # Interactive: vary the base rate
    print(f"\n  --- How base rate affects P(disease|+) ---")
    print(f"    {'Base rate':>12s}  {'P(disease|+)':>14s}")
    print(f"    {'─'*12}  {'─'*14}")
    for base in [0.0001, 0.001, 0.005, 0.01, 0.05, 0.1, 0.2, 0.5]:
        post = update_belief(base, p_positive_if_disease, p_positive_if_healthy)
        print(f"    {base:>12.4f}  {post:>14.4f}  ({post*100:.1f}%)")


def scenario_sentiment_analysis():
    """Bayesian sentiment classifier."""
    print("\n\n" + "=" * 65)
    print("  SCENARIO 3: NAIVE BAYES SENTIMENT CLASSIFIER")
    print("=" * 65)
    print()
    print("  Classify movie reviews as POSITIVE or NEGATIVE using word probabilities.")
    print("  'Naive' because it assumes words are independent (they're not, but it works!).")
    print()
    
    # Trained on a toy dataset
    p_positive = 0.6  # 60% of reviews are positive
    
    # P(word | positive) and P(word | negative)
    word_probs = {
        "great":     (0.15, 0.01),
        "amazing":   (0.10, 0.005),
        "bad":       (0.01, 0.12),
        "terrible":  (0.005, 0.10),
        "the":       (0.05, 0.05),   # neutral word
        "movie":     (0.06, 0.06),   # neutral word
        "loved":     (0.12, 0.01),
        "hated":     (0.005, 0.11),
    }
    
    def classify_review(words_in_review):
        """Classify a review using Naive Bayes."""
        prior_pos = p_positive
        prior_neg = 1.0 - p_positive
        
        # Start with priors (in log space for numerical stability)
        import math
        log_pos = math.log(prior_pos)
        log_neg = math.log(prior_neg)
        
        for word in words_in_review:
            if word in word_probs:
                p_w_pos, p_w_neg = word_probs[word]
                # Avoid log(0)
                log_pos += math.log(max(p_w_pos, 1e-10))
                log_neg += math.log(max(p_w_neg, 1e-10))
        
        # Convert back from log space (this is the "naive" part)
        # Use softmax-like normalization
        max_log = max(log_pos, log_neg)
        pos_score = math.exp(log_pos - max_log)
        neg_score = math.exp(log_neg - max_log)
        total = pos_score + neg_score
        
        return pos_score / total, neg_score / total
    
    test_reviews = [
        ["great", "amazing", "loved", "movie"],
        ["bad", "terrible", "hated", "movie"],
        ["great", "movie"],             # weak positive
        ["the", "movie"],               # neutral (no strong signal)
        ["great", "but", "terrible"],   # mixed — 'but' not in vocab
    ]
    
    print(f"  Training: P(positive) = {p_positive*100:.0f}%")
    print()
    print(f"  {'Review':<40s} {'P(pos)':>10s} {'P(neg)':>10s} {'CLASS':>10s}")
    print(f"  {'─'*40}  {'─'*10}  {'─'*10}  {'─'*10}")
    
    for review in test_reviews:
        p_pos, p_neg = classify_review(review)
        review_str = '"' + " ".join(review) + '"'
        cls = "POSITIVE" if p_pos > 0.5 else "NEGATIVE"
        print(f"  {review_str:<40s} {p_pos:>10.4f} {p_neg:>10.4f} {cls:>10s}")
    
    print()
    print("  KEY INSIGHT: Naive Bayes combines evidence from each word by")
    print("  MULTIPLYING their individual likelihood ratios. Strong sentiment")
    print("  words dominate. Neutral words like 'the' barely shift the scale.")


# =============================================================================
# INTERACTIVE MODE
# =============================================================================

def interactive_mode():
    """Let user plug in their own numbers."""
    print("\n\n" + "=" * 65)
    print("  INTERACTIVE BAYES CALCULATOR")
    print("=" * 65)
    print()
    print("  Enter your own numbers, or press Enter to use defaults.")
    print("  Bayes: P(A|B) = P(B|A)*P(A) / P(B)")
    print()
    
    try:
        prior_in = input("  P(A) — prior probability of A [0.2]: ").strip()
        prior = float(prior_in) if prior_in else 0.2
        
        likelihood_in = input("  P(B|A) — probability of evidence if A is true [0.5]: ").strip()
        likelihood = float(likelihood_in) if likelihood_in else 0.5
        
        print("\n  To compute P(B), we also need:")
        p_not_a = 1.0 - prior
        
        l_if_false_in = input(f"  P(B|not_A) — probability of evidence if A is false [0.05]: ").strip()
        likelihood_false = float(l_if_false_in) if l_if_false_in else 0.05
        
        p_b = total_probability(likelihood, prior, likelihood_false, p_not_a)
        posterior = bayes_theorem(prior, likelihood, p_b)
        
        print(f"\n  {'─'*40}")
        print(f"  P(B) = {likelihood}*{prior} + {likelihood_false}*{p_not_a:.1f}")
        print(f"       = {p_b:.4f}")
        print(f"\n  P(A|B) = {likelihood}*{prior} / {p_b:.4f}")
        print(f"         = {posterior:.4f}")
        print(f"         = {posterior*100:.1f}%")
        print(f"\n  Evidence B updated belief from {prior*100:.0f}% to {posterior*100:.1f}%")
        print(f"  {'─'*40}")
        
        if posterior > prior:
            print(f"  Evidence SUPPORTS hypothesis A (probability went UP)")
        else:
            print(f"  Evidence WEAKENS hypothesis A (probability went DOWN)")
        
    except (EOFError, KeyboardInterrupt):
        print("\n  (Skipping interactive mode)")
    except ValueError as e:
        print(f"  Invalid input: {e}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    scenario_spam_detection()
    scenario_medical_diagnosis()
    scenario_sentiment_analysis()
    
    # Only run interactive mode if not piped
    if sys.stdin.isatty():
        interactive_mode()
    else:
        print("\n  (Interactive mode skipped — run directly for interactive mode)")
    
    print("\n" + "=" * 65)
    print("  KEY TAKEAWAYS")
    print("=" * 65)
    print("""
  1. Bayes theorem UPDATES beliefs with evidence
  2. Base rates MATTER — a positive test doesn't always mean disease
  3. Multiple pieces of evidence can be combined sequentially
  4. Naive Bayes assumes independence — "naive" but useful
  5. This powers: spam filters, medical diagnosis, sentiment analysis,
     recommendation systems, and much more

  The formula is simple. The implications are profound.
""")
