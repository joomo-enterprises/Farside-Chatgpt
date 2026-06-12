#!/usr/bin/env python3
"""
Bias Detector — Episode 6: AI Ethics You Cannot Ignore
On The FarSide Series

Analyzes a dataset (dictionary format) and checks for representation
across demographic groups. Prints a bias report showing distribution
percentages, imbalance warnings, and recommendations.

Usage:
    python 01_bias_detector.py
"""

from typing import Any


def analyze_bias(
    dataset: dict[str, dict[str, int]],
    group_key: str = "applicants",
    protected_attributes: list[str] | None = None,
    imbalance_threshold: float = 3.0,
    underrepresentation_threshold: float = 5.0,
) -> dict[str, Any]:
    """
    Analyze a dataset for representation bias across demographic groups.

    Args:
        dataset: Nested dict. Outer key = category (e.g. 'applicants', 'approved').
                 Inner key = group name, value = count.
        group_key: Which outer key to use for demographic distribution analysis.
        protected_attributes: List of group names to check. If None, inferred from data.
        imbalance_threshold: Ratio above which a group is flagged as over-represented.
        underrepresentation_threshold: Percentage below which a group is flagged.

    Returns:
        Dictionary containing the full bias report.
    """
    if group_key not in dataset:
        raise ValueError(f"Key '{group_key}' not found in dataset. Available: {list(dataset.keys())}")

    groups = dataset[group_key]
    total = sum(groups.values())

    if total == 0:
        raise ValueError("Dataset is empty — all counts are zero.")

    # Calculate distribution
    distribution = {}
    for group, count in groups.items():
        distribution[group] = {
            "count": count,
            "percentage": (count / total) * 100,
        }

    # Determine protected attributes to check
    if protected_attributes is None:
        protected_attributes = list(groups.keys())

    # Calculate expected percentage (uniform distribution)
    num_groups = len(protected_attributes)
    expected_pct = 100.0 / num_groups if num_groups > 0 else 0

    # Detect imbalances
    warnings = []
    avg_count = total / num_groups if num_groups > 0 else 0

    for group in protected_attributes:
        if group not in distribution:
            warnings.append(f"MISSING: '{group}' not found in dataset")
            continue

        pct = distribution[group]["percentage"]
        count = distribution[group]["count"]

        # Check over-representation
        if avg_count > 0 and count > avg_count * imbalance_threshold:
            ratio = count / avg_count
            warnings.append(
                f"IMBALANCE: '{group}' representation ({pct:.1f}%) exceeds "
                f"{imbalance_threshold}x average (ratio: {ratio:.1f}x)"
            )

        # Check under-representation
        if pct < underrepresentation_threshold:
            warnings.append(
                f"UNDERREPRESENTED: '{group}' ({pct:.1f}% — below "
                f"{underrepresentation_threshold}% threshold)"
            )

    # Determine overall risk level
    if len(warnings) == 0:
        risk_level = "LOW"
    elif len(warnings) <= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    # Generate recommendations
    recommendations = []
    if risk_level in ("MEDIUM", "HIGH"):
        recommendations.append(
            "Collect more data for underrepresented groups before training."
        )
        recommendations.append(
            "Apply resampling or weighting strategies to balance classes."
        )
    if any("IMBALANCE" in w for w in warnings):
        recommendations.append(
            "Consider stratified sampling to prevent majority-group dominance."
        )
    if any("UNDERREPRESENTED" in w for w in warnings):
        recommendations.append(
            "Evaluate whether underrepresented groups have sufficient samples "
            "for the model to learn meaningful patterns."
        )
    if risk_level == "LOW":
        recommendations.append(
            "Dataset appears balanced. Continue monitoring during training."
        )

    return {
        "total_samples": total,
        "num_groups": num_groups,
        "distribution": distribution,
        "warnings": warnings,
        "risk_level": risk_level,
        "recommendations": recommendations,
    }


def print_report(report: dict[str, Any], dataset_name: str = "Unnamed Dataset") -> None:
    """Pretty-print a bias detection report to the terminal."""
    print("=" * 45)
    print("       BIAS DETECTION REPORT")
    print("=" * 45)
    print(f"Dataset: {dataset_name}")
    print(f"Total samples: {report['total_samples']:,}")
    print()

    # Distribution table
    print("--- Demographic Distribution ---")
    print(f"{'Group':<16} {'Count':>8} {'Percentage':>12}")
    print("-" * 40)
    for group, stats in report["distribution"].items():
        print(f"{group:<16} {stats['count']:>8,} {stats['percentage']:>11.1f}%")
    print()

    # Warnings
    if report["warnings"]:
        print("--- Warnings ---")
        for w in report["warnings"]:
            print(f"  ⚠️  {w}")
        print()

    # Risk level
    risk = report["risk_level"]
    risk_icon = {"LOW": "✅", "MEDIUM": "⚠️", "HIGH": "🔴"}.get(risk, "❓")
    print(f"Overall Bias Risk: {risk_icon} {risk}")
    print()

    # Recommendations
    print("--- Recommendations ---")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"  {i}. {rec}")
    print()
    print("=" * 45)


def main() -> None:
    """Run bias detection on sample datasets and print reports."""

    # ------------------------------------------------------------------
    # Dataset 1: Hiring data (heavily imbalanced — the main demo)
    # ------------------------------------------------------------------
    hiring_data = {
        "applicants": {
            "male": 8500,
            "female": 3200,
            "non_binary": 150,
        },
        "approved": {
            "male": 6800,
            "female": 2100,
            "non_binary": 80,
        },
    }

    report = analyze_bias(hiring_data, group_key="applicants", imbalance_threshold=1.5)
    print_report(report, dataset_name="sample_hiring_data")

    # ------------------------------------------------------------------
    # Dataset 2: Loan approval data (moderately imbalanced)
    # ------------------------------------------------------------------
    loan_data = {
        "applicants": {
            "white": 6200,
            "black": 1800,
            "hispanic": 1500,
            "asian": 1200,
            "other": 300,
        },
        "approved": {
            "white": 4960,
            "black": 1170,
            "hispanic": 975,
            "asian": 900,
            "other": 180,
        },
    }

    report2 = analyze_bias(loan_data, group_key="applicants")
    print_report(report2, dataset_name="loan_approval_data")

    # ------------------------------------------------------------------
    # Dataset 3: Balanced dataset (should pass cleanly)
    # ------------------------------------------------------------------
    balanced_data = {
        "applicants": {
            "group_a": 3400,
            "group_b": 3300,
            "group_c": 3300,
        },
        "approved": {
            "group_a": 2720,
            "group_b": 2640,
            "group_c": 2640,
        },
    }

    report3 = analyze_bias(balanced_data, group_key="applicants")
    print_report(report3, dataset_name="balanced_test_data")


if __name__ == "__main__":
    main()
