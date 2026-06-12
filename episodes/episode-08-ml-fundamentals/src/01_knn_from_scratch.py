"""
Episode 8 — k-Nearest Neighbors From Scratch
==============================================
Implements k-NN classification in pure Python.
Works with CSV data, computes Euclidean distance, predicts class.

Standard library only — no NumPy, no scikit-learn.
"""

import csv
import math
import random
from collections import Counter


# =============================================================================
# DISTANCE METRICS
# =============================================================================

def euclidean_distance(a, b):
    """Compute Euclidean distance between two points.
    
    d = sqrt(sum((a_i - b_i)^2))
    
    This is the most common distance metric in ML.
    It generalizes the Pythagorean theorem to N dimensions.
    """
    if len(a) != len(b):
        raise ValueError(f"Points must have same dimensions: {len(a)} vs {len(b)}")
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def manhattan_distance(a, b):
    """Manhattan (L1) distance: sum of absolute differences.
    
    More robust to outliers than Euclidean.
    Think of it as city-block distance — how many blocks to walk.
    """
    return sum(abs(ai - bi) for ai, bi in zip(a, b))


def minkowski_distance(a, b, p=3):
    """Generalized distance metric.
    
    p=1: Manhattan distance
    p=2: Euclidean distance
    p->inf: Chebyshev distance (max difference)
    """
    return sum(abs(ai - bi) ** p for ai, bi in zip(a, b)) ** (1.0 / p)


# =============================================================================
# K-NN CLASSIFIER
# =============================================================================

class KNearestNeighbors:
    """k-Nearest Neighbors classifier.
    
    This is a 'lazy learner' — it doesn't train at all.
    It just stores the data and computes distances at prediction time.
    
    Parameters:
        k:           Number of neighbors to consider
        distance_fn: Distance metric function
    """
    
    def __init__(self, k=3, distance_fn=euclidean_distance):
        self.k = k
        self.distance_fn = distance_fn
        self.X_train = None
        self.y_train = None
    
    def fit(self, X, y):
        """Store the training data. That's it — no computation needed!"""
        self.X_train = X
        self.y_train = y
        return self
    
    def _predict_single(self, x):
        """Predict the class of a single data point."""
        # Compute distance to every training point
        distances = []
        for i, x_train in enumerate(self.X_train):
            dist = self.distance_fn(x, x_train)
            distances.append((dist, self.y_train[i], i))
        
        # Sort by distance and take the k nearest
        distances.sort(key=lambda d: d[0])
        k_nearest = distances[:self.k]
        
        # Majority vote
        k_labels = [label for _, label, _ in k_nearest]
        vote_counts = Counter(k_labels)
        most_common = vote_counts.most_common(1)[0][0]
        
        return most_common, k_nearest
    
    def predict(self, X):
        """Predict classes for multiple data points."""
        predictions = []
        for x in X:
            pred, _ = self._predict_single(x)
            predictions.append(pred)
        return predictions
    
    def predict_proba(self, x):
        """Return probability distribution over classes for a single point."""
        _, k_nearest = self._predict_single(x)
        k_labels = [label for _, label, _ in k_nearest]
        counts = Counter(k_labels)
        total = sum(counts.values())
        return {cls: count / total for cls, count in counts.items()}
    
    def score(self, X, y):
        """Compute accuracy on a dataset."""
        predictions = self.predict(X)
        correct = sum(1 for pred, actual in zip(predictions, y) if pred == actual)
        return correct / len(y)


# =============================================================================
# DATA UTILITIES
# =============================================================================

def load_csv(filepath, target_column=-1, feature_columns=None, has_header=True):
    """Load a CSV file and separate features from labels.
    
    Parameters:
        filepath:        Path to CSV file
        target_column:   Index of the label column (default: last column)
        feature_columns: List of feature column indices (default: all except target)
        has_header:      Whether the first row is a header
    
    Returns:
        X: List of feature vectors (each is a list of floats)
        y: List of labels (strings)
        feature_names: List of feature name strings
    """
    X = []
    y = []
    feature_names = None
    
    with open(filepath, 'r', newline='') as f:
        reader = csv.reader(f)
        
        if has_header:
            header = next(reader)
            if feature_columns is None:
                feature_columns = [i for i in range(len(header)) if i != target_column % len(header)]
            feature_names = [header[i] for i in feature_columns]
        
        for row in reader:
            if not row or all(cell.strip() == '' for cell in row):
                continue
            
            if feature_columns is None:
                feature_columns = list(range(len(row) - 1))
                target_column = len(row) - 1
            
            features = [float(row[i]) for i in feature_columns]
            label = row[target_column]
            
            X.append(features)
            y.append(label)
    
    return X, y, feature_names


def generate_iris_like_data(n_samples=150):
    """Generate a synthetic dataset similar to Iris for testing.
    
    Three classes with 4 features each.
    Uses deterministic pseudo-random generation for reproducibility.
    """
    random.seed(42)
    
    classes = ["setosa", "versicolor", "virginica"]
    # Feature means for each class: [sepal_len, sepal_wid, petal_len, petal_wid]
    class_params = {
        "setosa":     {"mean": [5.0, 3.4, 1.5, 0.2], "std": [0.35, 0.38, 0.17, 0.1]},
        "versicolor": {"mean": [5.9, 2.8, 4.3, 1.3], "std": [0.52, 0.31, 0.47, 0.2]},
        "virginica":  {"mean": [6.6, 3.0, 5.6, 2.0], "std": [0.64, 0.32, 0.55, 0.27]},
    }
    
    X = []
    y = []
    samples_per_class = n_samples // len(classes)
    
    for cls in classes:
        params = class_params[cls]
        for _ in range(samples_per_class):
            features = [
                random.gauss(mu, sigma)
                for mu, sigma in zip(params["mean"], params["std"])
            ]
            X.append(features)
            y.append(cls)
    
    # Shuffle
    combined = list(zip(X, y))
    random.shuffle(combined)
    X, y = zip(*combined)
    
    return list(X), list(y)


def train_test_split(X, y, test_ratio=0.2, seed=None):
    """Split data into training and test sets."""
    if seed is not None:
        random.seed(seed)
    
    indices = list(range(len(X)))
    random.shuffle(indices)
    
    split = int(len(X) * (1 - test_ratio))
    
    train_idx = indices[:split]
    test_idx = indices[split:]
    
    X_train = [X[i] for i in train_idx]
    y_train = [y[i] for i in train_idx]
    X_test = [X[i] for i in test_idx]
    y_test = [y[i] for i in test_idx]
    
    return X_train, X_test, y_train, y_test


def normalize(X):
    """Min-max normalization: scale all features to [0, 1].
    
    Critical for k-NN because it uses distance metrics.
    Without normalization, features with larger ranges dominate.
    """
    if not X:
        return X
    
    n_features = len(X[0])
    mins = [min(row[i] for row in X) for i in range(n_features)]
    maxs = [max(row[i] for row in X) for i in range(n_features)]
    
    normalized = []
    for row in X:
        norm_row = []
        for i in range(n_features):
            range_val = maxs[i] - mins[i]
            if range_val == 0:
                norm_row.append(0.0)
            else:
                norm_row.append((row[i] - mins[i]) / range_val)
        normalized.append(norm_row)
    
    return normalized


# =============================================================================
# DEMO: K-NN IN ACTION
# =============================================================================

def demo_knn_basic():
    """Basic k-NN demo with synthetic data."""
    print("=" * 65)
    print("  k-NEAREST NEIGHBORS: Basic Demo")
    print("=" * 65)
    print()
    
    # Simple 2D data: two classes
    # Class A: points near (2, 2)
    # Class B: points near (6, 6)
    X_train = [
        [1.5, 2.0], [2.0, 1.5], [2.5, 2.5], [1.8, 2.8], [2.2, 1.8],  # Class A
        [5.5, 6.0], [6.0, 5.5], [6.5, 6.5], [5.8, 6.8], [6.2, 5.8],  # Class B
    ]
    y_train = ["A", "A", "A", "A", "A", "B", "B", "B", "B", "B"]
    
    print("  Training data (2D points, 2 classes):")
    for x, y in zip(X_train, y_train):
        print(f"    ({x[0]:.1f}, {x[1]:.1f}) -> class {y}")
    
    # Test points
    test_points = [
        [2.0, 2.0],   # Clearly A
        [6.0, 6.0],   # Clearly B
        [4.0, 4.0],   # Right in the middle — ambiguous!
        [3.0, 3.0],   # Slightly toward A
    ]
    
    print("\n  Predictions with k=3:")
    knn = KNearestNeighbors(k=3)
    knn.fit(X_train, y_train)
    
    print(f"    {'Point':>12s}  {'Prediction':>12s}  {'Probabilities':>30s}")
    print(f"    {'─'*12}  {'─'*12}  {'─'*30}")
    
    for point in test_points:
        pred, neighbors = knn._predict_single(point)
        proba = knn.predict_proba(point)
        proba_str = ", ".join(f"{c}:{p:.1%}" for c, p in sorted(proba.items()))
        print(f"    ({point[0]:.0f}, {point[1]:.0f})      {pred:>12s}  {proba_str:>30s}")
    
    # Show the neighbors for the ambiguous point
    print("\n  Neighbors for point (4, 4) — the ambiguous one:")
    _, neighbors = knn._predict_single([4.0, 4.0])
    print(f"    {'Rank':>4s}  {'Point':>12s}  {'Distance':>10s}  {'Class':>6s}")
    print(f"    {'─'*4}  {'─'*12}  {'─'*10}  {'─'*6}")
    for rank, (dist, label, idx) in enumerate(neighbors, 1):
        pt = X_train[idx]
        print(f"    {rank:4d}  ({pt[0]:.1f}, {pt[1]:.1f})    {dist:10.4f}  {label:>6s}")


def demo_knn_iris():
    """k-NN on a larger synthetic dataset."""
    print("\n\n" + "=" * 65)
    print("  k-NEAREST NEIGHBORS: Synthetic Iris Dataset")
    print("=" * 65)
    print()
    
    X, y = generate_iris_like_data(n_samples=150)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_ratio=0.25, seed=42)
    
    print(f"  Dataset: {len(X)} samples, {len(X[0])} features, {len(set(y))} classes")
    print(f"  Train: {len(X_train)} samples, Test: {len(X_test)} samples")
    print(f"  Classes: {sorted(set(y))}")
    print()
    
    # Test different k values
    print("  Effect of k on accuracy:")
    print(f"    {'k':>4s}  {'Accuracy':>10s}  {'Notes':>30s}")
    print(f"    {'─'*4}  {'─'*10}  {'─'*30}")
    
    for k in [1, 3, 5, 7, 9, 15, 21]:
        knn = KNearestNeighbors(k=k)
        knn.fit(X_train, y_train)
        acc = knn.score(X_test, y_test)
        
        notes = ""
        if k == 1:
            notes = "(memorizes training data)"
        elif k == 3:
            notes = "(good default)"
        elif k >= 21:
            notes = "(too smooth, underfits)"
        
        bar = "#" * int(acc * 30)
        print(f"    {k:4d}  {acc:>10.2%}  {bar:<30s}  {notes}")
    
    # Detailed results with best k
    best_k = 5
    knn = KNearestNeighbors(k=best_k)
    knn.fit(X_train, y_train)
    predictions = knn.predict(X_test)
    
    print(f"\n  Detailed results (k={best_k}):")
    print(f"    {'Actual':>15s}  {'Predicted':>15s}  {'Correct':>8s}")
    print(f"    {'─'*15}  {'─'*15}  {'─'*8}")
    
    correct = 0
    for pred, actual in zip(predictions, y_test):
        is_correct = pred == actual
        correct += is_correct
        mark = "OK" if is_correct else "WRONG"
        print(f"    {actual:>15s}  {pred:>15s}  {mark:>8s}")
    
    print(f"\n  Accuracy: {correct}/{len(y_test)} = {correct/len(y_test):.2%}")


def demo_knn_distance_metrics():
    """Compare different distance metrics."""
    print("\n\n" + "=" * 65)
    print("  DISTANCE METRICS COMPARISON")
    print("=" * 65)
    print()
    
    a = [1.0, 2.0, 3.0]
    b = [4.0, 6.0, 3.0]
    
    print(f"  Point A: {a}")
    print(f"  Point B: {b}")
    print()
    print(f"  Euclidean distance:  {euclidean_distance(a, b):.4f}")
    print(f"  Manhattan distance:  {manhattan_distance(a, b):.4f}")
    print(f"  Minkowski (p=1):     {minkowski_distance(a, b, p=1):.4f}  (= Manhattan)")
    print(f"  Minkowski (p=2):     {minkowski_distance(a, b, p=2):.4f}  (= Euclidean)")
    print(f"  Minkowski (p=3):     {minkowski_distance(a, b, p=3):.4f}")
    print()
    print("  KEY INSIGHT: Euclidean is most common, but Manhattan is")
    print("  more robust to outliers. For high-dimensional data,")
    print("  cosine similarity often works better than either.")


def demo_csv_workflow():
    """Show how to use k-NN with CSV data."""
    print("\n\n" + "=" * 65)
    print("  CSV DATA WORKFLOW")
    print("=" * 65)
    print()
    
    # Create a sample CSV file
    csv_path = "/mnt/c/k/author/farside-chatgpt-youtube/episodes/episode-08-ml-fundamentals/src/sample_data.csv"
    
    print("  Creating sample CSV dataset...")
    header = ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]
    
    X, y = generate_iris_like_data(n_samples=60)
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for features, label in zip(X, y):
            writer.writerow(features + [label])
    
    print(f"  Written to: {csv_path}")
    print(f"  Rows: {len(X)}, Columns: {len(header)}")
    print()
    
    # Load it back
    X_loaded, y_loaded, feature_names = load_csv(csv_path, target_column=-1)
    
    print(f"  Loaded from CSV:")
    print(f"    Features: {feature_names}")
    print(f"    Samples: {len(X_loaded)}")
    print(f"    Classes: {sorted(set(y_loaded))}")
    print(f"    First sample: {X_loaded[0]} -> {y_loaded[0]}")
    print()
    
    # Train and evaluate
    X_train, X_test, y_train, y_test = train_test_split(X_loaded, y_loaded, test_ratio=0.25, seed=123)
    
    knn = KNearestNeighbors(k=5)
    knn.fit(X_train, y_train)
    acc = knn.score(X_test, y_test)
    
    print(f"  k-NN (k=5) accuracy on held-out test set: {acc:.2%}")
    print(f"  This is the real workflow: load CSV -> split -> train -> evaluate")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    demo_knn_basic()
    demo_knn_iris()
    demo_knn_distance_metrics()
    demo_csv_workflow()
    
    print("\n" + "=" * 65)
    print("  k-NN SUMMARY")
    print("=" * 65)
    print("""
  k-Nearest Neighbors is the simplest ML algorithm:
  
  1. Store training data (no training needed!)
  2. For a new point, find the k closest training points
  3. Take a majority vote
  
  Pros: Simple, no training time, naturally handles multi-class
  Cons: Slow at prediction time, sensitive to irrelevant features
  
  Key decisions:
  - k: odd number to avoid ties (3 or 5 are good defaults)
  - Distance metric: Euclidean is standard, Manhattan for robustness
  - Feature scaling: ALWAYS normalize your features!
  
  Despite its simplicity, k-NN is competitive with much more
  complex algorithms on many real-world problems.
""")
