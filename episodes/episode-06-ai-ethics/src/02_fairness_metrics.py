#!/usr/bin/env python3
"""
Fairness Metrics Calculator — Episode 6: AI Ethics You Cannot Ignore
On The FarSide Series

Computes three standard fairness metrics using mock classification data:
  1. Demographic Parity
  2. Equalized Odds (FPR and FNR parity)
  3. Predictive Parity (PPV parity)

All calculations use standard library only.

Usage:
    python 02_fairness_metrics.py
"""

from dataclasses import dataclass, field


@dataclass
class GroupOutcome:
    """Confusion matrix counts for a single demographic group."""
    group_name: str
    true_positives: int = 0   # Correctly predicted positive
    true_negatives: int = 0   # Correctly predicted negative
    false_positives: int = 0  # Incorrectly predicted positive
    false_negatives: int = 0  # Incorrectly predicted negative

    @property
    def total(self) -> int:
        return self.true_positives + self.true_negatives + self.false_positives + self.false_negatives

    @property
    def predicted_positive(self) -> int:
        return self.true_positives + self.false_positives

    @property
    def predicted_negative(self) -> int:
        return self.true_negatives + self.false_negatives

    @property
    def actual_positive(self) -> int:
        return self.true_positives + self.false_negatives

    @property
    def actual_negative(self) -> int:
        return self.true_negatives + self.false_positives

    @property
    def tpr(self) -> float:
        """True Positive Rate (Recall / Sensitivity)."""
        denom = self.actual_positive
        return self.true_positives / denom if denom > 0 else 0.0

    @property
    def fpr(self) -> float:
        """False Positive Rate."""
        denom = self.actual_negative
        return self.false_positives / denom if denom > 0 else 0.0

    @property
    def fnr(self) -> float:
        """False Negative Rate."""
        denom = self.actual_positive
        return self.false_negatives / denom if denom > 0 else 0.0

    @property
    def tnr(self) -> float:
        """True Negative Rate (Specificity)."""
        denom = self.actual_negative
        return self.true_negatives / denom if denom > 0 else 0.0

    @property
    def ppv(self) -> float:
        """Positive Predictive Value (Precision)."""
        denom = self.predicted_positive
        return self.true_positives / denom if denom > 0 else 0.0

    def approval_rate(self) -> float:
        """P(Approved) — fraction of group predicted as positive."""
        return self.predicted_positive / self.total if self.total > 0 else 0.0


@dataclass
class FairnessReport:
    """Aggregated fairness metrics across all groups."""
    groups: list[GroupOutcome] = field(default_factory=list)
    demographic_parity_threshold: float = 0.10
    equalized_odds_threshold: float = 0.05
    predictive_parity_threshold: float = 0.10

    # Results
    demographic_parity_satisfied: bool = True
    demographic_parity_diff: float = 0.0
    approval_rates: dict[str, float] = field(default_factory=dict)

    equalized_odds_satisfied: bool = True
    max_fpr_diff: float = 0.0
    max_fnr_diff: float = 0.0

    predictive_parity_satisfied: bool = True
    predictive_parity_diff: float = 0.0
    ppv_values: dict[str, float] = field(default_factory=dict)

    def compute(self) -> None:
        """Run all fairness metric calculations."""
        self._compute_demographic_parity()
        self._compute_equalized_odds()
        self._compute_predictive_parity()

    def _compute_demographic_parity(self) -> None:
        """
        Demographic Parity: P(Ŷ=1 | A=a) should be equal across all groups a.
        We compute the max difference between any two groups' approval rates.
        """
        self.approval_rates = {g.group_name: g.approval_rate() for g in self.groups}
        rates = list(self.approval_rates.values())
        if len(rates) >= 2:
            self.demographic_parity_diff = max(rates) - min(rates)
        self.demographic_parity_satisfied = (
            self.demographic_parity_diff <= self.demographic_parity_threshold
        )

    def _compute_equalized_odds(self) -> None:
        """
        Equalized Odds: FPR and FNR should be equal across groups.
        We check the max difference in FPR and max difference in FNR.
        """
        fpr_values = {g.group_name: g.fpr for g in self.groups}
        fnr_values = {g.group_name: g.fnr for g in self.groups}

        fpr_vals = list(fpr_values.values())
        fnr_vals = list(fnr_values.values())

        if len(fpr_vals) >= 2:
            self.max_fpr_diff = max(fpr_vals) - min(fpr_vals)
        if len(fnr_vals) >= 2:
            self.max_fnr_diff = max(fnr_vals) - min(fnr_vals)

        # Both FPR and FNR differences must be within threshold
        self.equalized_odds_satisfied = (
            self.max_fpr_diff <= self.equalized_odds_threshold
            and self.max_fnr_diff <= self.equalized_odds_threshold
        )

    def _compute_predictive_parity(self) -> None:
        """
        Predictive Parity: PPV (precision) should be equal across groups.
        We check the max difference in PPV between any two groups.
        """
        self.ppv_values = {g.group_name: g.ppv for g in self.groups}
        ppv_vals = list(self.ppv_values.values())
        if len(ppv_vals) >= 2:
            self.predictive_parity_diff = max(ppv_vals) - min(ppv_vals)
        self.predictive_parity_satisfied = (
            self.predictive_parity_diff <= self.predictive_parity_threshold
        )

    @property
    def all_satisfied(self) -> bool:
        return (
            self.demographic_parity_satisfied
            and self.equalized_odds_satisfied
            and self.predictive_parity_satisfied
        )

    def print_report(self) -> None:
        """Pretty-print the full fairness metrics report."""
        print("=" * 50)
        print("       FAIRNESS METRICS ANALYSIS")
        print("=" * 50)
        print("Mock Data: Hiring Decisions by Gender")
        print()

        # --- Demographic Parity ---
        print("--- Demographic Parity ---")
        print("P(Approved | group) for each demographic:")
        for group, rate in self.approval_rates.items():
            print(f"  P(Approved | {group:<12}) = {rate:.3f}")
        print()
        status = "✅ SATISFIED" if self.demographic_parity_satisfied else "❌ NOT SATISFIED"
        print(f"Demographic Parity Difference: {self.demographic_parity_diff:.3f}")
        print(f"  (threshold: {self.demographic_parity_threshold}) → {status}")
        print()

        # --- Equalized Odds ---
        print("--- Equalized Odds ---")
        print(f"{'Group':<12} {'FPR':>8} {'FNR':>8}")
        print("-" * 32)
        for g in self.groups:
            print(f"{g.group_name:<12} {g.fpr:>8.3f} {g.fnr:>8.3f}")
        print()
        print(f"Max FPR difference: {self.max_fpr_diff:.3f}")
        print(f"Max FNR difference: {self.max_fnr_diff:.3f}")
        eo_status = "✅ SATISFIED" if self.equalized_odds_satisfied else "❌ NOT SATISFIED"
        print(f"  (threshold: {self.equalized_odds_threshold}) → {eo_status}")
        print()

        # --- Predictive Parity ---
        print("--- Predictive Parity ---")
        print("PPV (precision) by group:")
        for group, ppv in self.ppv_values.items():
            print(f"  {group:<12}: {ppv:.2f}")
        print()
        pp_status = "✅ SATISFIED" if self.predictive_parity_satisfied else "❌ NOT SATISFIED"
        print(f"Predictive Parity Difference: {self.predictive_parity_diff:.2f}")
        print(f"  (threshold: {self.predictive_parity_threshold}) → {pp_status}")
        print()

        # --- Verdict ---
        print("=" * 50)
        if self.all_satisfied:
            print("  ✅ VERDICT: Model PASSES all fairness metrics")
        else:
            failed = []
            if not self.demographic_parity_satisfied:
                failed.append("Demographic Parity")
            if not self.equalized_odds_satisfied:
                failed.append("Equalized Odds")
            if not self.predictive_parity_satisfied:
                failed.append("Predictive Parity")
            print(f"  ❌ VERDICT: Model FAILS fairness metrics")
            print(f"  Failed: {', '.join(failed)}")
        print("=" * 50)
        print()

        # --- Recommendations ---
        print("--- Recommendations ---")
        if not self.all_satisfied:
            print("  1. Review training data for representation bias.")
            print("  2. Apply fairness constraints during training (e.g., reweighting,")
            print("     adversarial debiasing, or post-processing calibration).")
            print("  3. Re-evaluate after mitigation with this same script.")
            print("  4. Consult domain experts and affected communities")
            print("     before deploying.")
        else:
            print("  All metrics within thresholds. Continue monitoring in production.")
            print("  Re-run this analysis periodically on live prediction data.")
        print()


def build_mock_biased_data() -> list[GroupOutcome]:
    """
    Build a mock dataset that intentionally demonstrates bias.
    Based on a fictional hiring tool with 3 gender groups.

    GroupSizes:
      - male:    800 applicants  (actual qualified: 560)
      - female:  600 applicants  (actual qualified: 420)
      - other:   200 applicants  (actual qualified: 120)

    The model is biased: it approves males at a higher rate and
    makes more errors on non-male groups.
    """
    outcomes = [
        GroupOutcome(
            group_name="male",
            true_positives=500,   # correctly approved qualified men
            true_negatives=180,   # correctly rejected unqualified men
            false_positives=80,   # wrongly approved unqualified men
            false_negatives=140,  # wrongly rejected qualified men
        ),
        GroupOutcome(
            group_name="female",
            true_positives=300,   # correctly approved qualified women
            true_negatives=120,   # correctly rejected unqualified women
            false_positives=90,   # wrongly approved unqualified women
            false_negatives=90,   # wrongly rejected qualified women
        ),
        GroupOutcome(
            group_name="other",
            true_positives=70,    # correctly approved qualified non-binary
            true_negatives=50,    # correctly rejected unqualified non-binary
            false_positives=50,   # wrongly approved unqualified non-binary
            false_negatives=30,   # wrongly rejected qualified non-binary
        ),
    ]
    return outcomes


def build_mock_fair_data() -> list[GroupOutcome]:
    """
    Build a mock dataset where the model is roughly fair across groups.
    This serves as a contrast to the biased example.
    """
    outcomes = [
        GroupOutcome(
            group_name="male",
            true_positives=420,
            true_negatives=240,
            false_positives=60,
            false_negatives=80,
        ),
        GroupOutcome(
            group_name="female",
            true_positives=400,
            true_negatives=220,
            false_positives=55,
            false_negatives=75,
        ),
        GroupOutcome(
            group_name="other",
            true_positives=380,
            true_negatives=200,
            false_positives=50,
            false_negatives=70,
        ),
    ]
    return outcomes


def main() -> None:
    """Run fairness metrics on mock datasets and print reports."""

    # ==================================================================
    # Dataset 1: Biased model (should FAIL metrics)
    # ==================================================================
    print("\n" + "█" * 50)
    print("  DATASET 1: BIASED HIRING MODEL")
    print("█" * 50 + "\n")

    biased_groups = build_mock_biased_data()
    report1 = FairnessReport(groups=biased_groups)
    report1.compute()
    report1.print_report()

    # ==================================================================
    # Dataset 2: Fairer model (should PASS metrics)
    # ==================================================================
    print("\n" + "█" * 50)
    print("  DATASET 2: IMPROVED HIRING MODEL")
    print("█" * 50 + "\n")

    fair_groups = build_mock_fair_data()
    report2 = FairnessReport(groups=fair_groups)
    report2.compute()
    report2.print_report()


if __name__ == "__main__":
    main()
