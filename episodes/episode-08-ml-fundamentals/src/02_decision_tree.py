"""
Episode 8 — Decision Tree From Scratch
=======================================
Simple decision tree classifier using entropy and information gain.
Pure Python — no external dependencies.

Decision trees ask sequential yes/no questions about features,
splitting data to maximize information gain at each step.
"""

import math
import random
from collections import Counter


# =============================================================================
# ENTROPY & INFORMATION GAIN
# =============================================================================

def entropy(labels):
    """Compute Shannon entropy of a label distribution.
    
    H = -sum(p_i * log2(p_i))
    
    Entropy measures impurity or uncertainty:
    - 0.0 = perfectly pure (all same class)
    - 1.0 = maximum impurity (50/50 split for binary)
    - Higher = more mixed
    
    This is the same concept from information theory and physics.
    """
    if not labels:
        return 0.0
    
    counts = Counter(labels)
    total = len(labels)
    
    h = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            h -= p * math.log2(p)
    
    return h


def information_gain(parent_labels, left_labels, right_labels):
    """Compute information gain from a split.
    
    IG = H(parent) - weighted_avg(H(left), H(right))
    
    Higher gain = better split = more useful question.
    The algorithm picks the split with the highest information gain.
    """
    n = len(parent_labels)
    n_left = len(left_labels)
    n_right = len(right_labels)
    
    if n == 0:
        return 0.0
    
    parent_entropy = entropy(parent_labels)
    left_entropy = entropy(left_labels) if n_left > 0 else 0.0
    right_entropy = entropy(right_labels) if n_right > 0 else 0.0
    
    weighted_child_entropy = (n_left / n) * left_entropy + (n_right / n) * right_entropy
    
    return parent_entropy - weighted_child_entropy


# =============================================================================
# DECISION TREE NODE
# =============================================================================

class TreeNode:
    """A node in the decision tree.
    
    Internal nodes: have a feature index, threshold, and two children
    Leaf nodes: have a prediction (class label) and class probabilities
    """
    
    def __init__(self):
        self.feature_index = None   # Which feature to split on
        self.threshold = None        # Threshold value for the split
        self.left = None             # Left child (feature <= threshold)
        self.right = None            # Right child (feature > threshold)
        self.prediction = None       # Class prediction (leaf nodes only)
        self.probabilities = None    # Class probabilities (leaf nodes only)
        self.is_leaf = False
        self.samples = 0             # Number of training samples at this node
        self.depth = 0               # Depth in the tree


# =============================================================================
# DECISION TREE CLASSIFIER
# =============================================================================

class DecisionTreeClassifier:
    """Decision tree classifier built from scratch.
    
    Parameters:
        max_depth:        Maximum depth of the tree (prevents overfitting)
        min_samples_split: Minimum samples required to split a node
        min_samples_leaf:  Minimum samples required in a leaf node
    """
    
    def __init__(self, max_depth=5, min_samples_split=2, min_samples_leaf=1):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.root = None
        self.n_features = None
        self.n_classes = None
    
    def fit(self, X, y):
        """Build the decision tree from training data."""
        self.n_features = len(X[0])
        self.n_classes = len(set(y))
        self.root = self._build_tree(X, y, depth=0)
        return self
    
    def _build_tree(self, X, y, depth):
        """Recursively build the tree."""
        node = TreeNode()
        node.samples = len(y)
        node.depth = depth
        
        # Count class distribution
        counts = Counter(y)
        node.probabilities = {cls: count / len(y) for cls, count in counts.items()}
        node.prediction = counts.most_common(1)[0][0]
        
        # Check stopping conditions
        if (depth >= self.max_depth or
            len(y) < self.min_samples_split or
            len(set(y)) == 1):
            node.is_leaf = True
            return node
        
        # Find the best split
        best_gain = -1
        best_feature = None
        best_threshold = None
        best_left_idx = None
        best_right_idx = None
        
        for feature_idx in range(self.n_features):
            # Get unique values for this feature to try as thresholds
            values = sorted(set(row[feature_idx] for row in X))
            
            # Try midpoints between consecutive values
            thresholds = []
            for i in range(len(values) - 1):
                thresholds.append((values[i] + values[i + 1]) / 2.0)
            
            if not thresholds:
                thresholds = values
            
            for threshold in thresholds:
                left_idx = [i for i, row in enumerate(X) if row[feature_idx] <= threshold]
                right_idx = [i for i, row in enumerate(X) if row[feature_idx] > threshold]
                
                # Check minimum leaf size
                if len(left_idx) < self.min_samples_leaf or len(right_idx) < self.min_samples_leaf:
                    continue
                
                left_labels = [y[i] for i in left_idx]
                right_labels = [y[i] for i in right_idx]
                
                gain = information_gain(y, left_labels, right_labels)
                
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature_idx
                    best_threshold = threshold
                    best_left_idx = left_idx
                    best_right_idx = right_idx
        
        # If no good split found, make a leaf
        if best_gain <= 0 or best_feature is None:
            node.is_leaf = True
            return node
        
        # Create the split
        node.feature_index = best_feature
        node.threshold = best_threshold
        
        # Recursively build children
        left_X = [X[i] for i in best_left_idx]
        left_y = [y[i] for i in best_left_idx]
        right_X = [X[i] for i in best_right_idx]
        right_y = [y[i] for i in best_right_idx]
        
        node.left = self._build_tree(left_X, left_y, depth + 1)
        node.right = self._build_tree(right_X, right_y, depth + 1)
        
        return node
    
    def _predict_single(self, x, node):
        """Traverse the tree to classify a single point."""
        if node.is_leaf:
            return node.prediction, node.probabilities
        
        if x[node.feature_index] <= node.threshold:
            return self._predict_single(x, node.left)
        else:
            return self._predict_single(x, node.right)
    
    def predict(self, X):
        """Predict classes for multiple data points."""
        return [self._predict_single(x, self.root)[0] for x in X]
    
    def predict_proba(self, x):
        """Return class probabilities for a single point."""
        return self._predict_single(x, self.root)[1]
    
    def score(self, X, y):
        """Compute accuracy."""
        predictions = self.predict(X)
        correct = sum(1 for p, a in zip(predictions, y) if p == a)
        return correct / len(y)
    
    def print_tree(self, feature_names=None, node=None, indent=""):
        """Print the tree structure — decision trees are interpretable!"""
        if node is None:
            node = self.root
            print("\n  Decision Tree Structure:")
            print("  " + "─" * 50)
        
        if node.is_leaf:
            prob_str = ", ".join(f"{c}:{p:.0%}" for c, p in sorted(node.probabilities.items()))
            print(f"{indent}-> PREDICT: {node.prediction} ({prob_str}) [{node.samples} samples]")
            return
        
        feat_name = feature_names[node.feature_index] if feature_names else f"feature[{node.feature_index}]"
        
        print(f"{indent}[{feat_name} <= {node.threshold:.3f}]  (gain from this split)")
        print(f"{indent} ├── YES:")
        self.print_tree(feature_names, node.left, indent + " │   ")
        print(f"{indent} └── NO:")
        self.print_tree(feature_names, node.right, indent + "    ")


# =============================================================================
# DEMO
# =============================================================================

def demo_entropy():
    """Demonstrate entropy concept."""
    print("=" * 65)
    print("  ENTROPY: Measuring Uncertainty")
    print("=" * 65)
    print()
    
    examples = [
        (["cat"] * 10, "All cats (pure)"),
        (["cat"] * 5 + ["dog"] * 5, "50/50 cats and dogs (max impurity)"),
        (["cat"] * 7 + ["dog"] * 3, "70/30 cats and dogs"),
        (["cat"] * 9 + ["dog"] * 1, "90/10 cats and dogs"),
        (["cat"] * 3 + ["dog"] * 3 + ["bird"] * 3 + ["fish"] * 1, "Mixed 4 classes"),
    ]
    
    print("  Entropy measures how MIXED a group is:")
    print(f"    {'Distribution':>40s}  {'Entropy':>10s}  {'Purity':>10s}")
    print(f"    {'─'*40}  {'─'*10}  {'─'*10}")
    
    for labels, desc in examples:
        h = entropy(labels)
        purity = "pure" if h == 0 else ("mixed" if h > 0.8 else "mostly pure")
        print(f"    {desc:>40s}  {h:>10.4f}  {purity:>10s}")
    
    print()
    print("  Lower entropy = more pure = better for a leaf node.")
    print("  The tree tries to SPLIT data to REDUCE entropy.")


def demo_decision_tree_2d():
    """Demo with simple 2D data."""
    print("\n\n" + "=" * 65)
    print("  DECISION TREE: Simple 2D Classification")
    print("=" * 65)
    print()
    
    # Simple dataset: predict whether to play tennis based on weather
    # Features: [temperature, humidity] (normalized 0-1)
    # Labels: "play" or "no"
    X = [
        [0.9, 0.8],   # hot, humid -> no
        [0.85, 0.9],  # hot, humid -> no
        [0.3, 0.7],   # cool, humid -> yes
        [0.2, 0.3],   # cool, normal -> yes
        [0.1, 0.8],   # cold, humid -> no
        [0.15, 0.2],  # cold, normal -> yes
        [0.5, 0.5],   # mild, normal -> yes
        [0.6, 0.9],   # mild, humid -> no
        [0.4, 0.4],   # cool, normal -> yes
        [0.7, 0.3],   # mild, normal -> yes
    ]
    y = ["no", "no", "yes", "yes", "no", "yes", "yes", "no", "yes", "yes"]
    
    feature_names = ["temperature", "humidity"]
    
    print("  Training data (should we play tennis?):")
    print(f"    {'Temp':>8s}  {'Humidity':>10s}  {'Play?':>6s}")
    print(f"    {'─'*8}  {'─'*10}  {'─'*6}")
    for features, label in zip(X, y):
        print(f"    {features[0]:>8.2f}  {features[1]:>10.2f}  {label:>6s}")
    
    # Build tree
    tree = DecisionTreeClassifier(max_depth=3)
    tree.fit(X, y)
    
    # Print the tree
    tree.print_tree(feature_names)
    
    # Test predictions
    print("\n  Predictions on new data:")
    test_points = [
        ([0.95, 0.95], "very hot, very humid"),
        ([0.1, 0.1], "cold, dry"),
        ([0.5, 0.5], "mild, moderate"),
    ]
    
    for point, desc in test_points:
        pred = tree.predict([point])[0]
        proba = tree.predict_proba(point)
        proba_str = ", ".join(f"{c}:{p:.0%}" for c, p in sorted(proba.items()))
        print(f"    {desc:>25s} -> {pred}  ({proba_str})")
    
    # Training accuracy
    acc = tree.score(X, y)
    print(f"\n  Training accuracy: {acc:.0%}")


def demo_decision_tree_iris():
    """Demo with larger synthetic dataset."""
    print("\n\n" + "=" * 65)
    print("  DECISION TREE: Synthetic Iris Dataset")
    print("=" * 65)
    print()
    
    random.seed(42)
    
    # Generate synthetic data
    classes = ["setosa", "versicolor", "virginica"]
    class_params = {
        "setosa":     {"mean": [5.0, 3.4, 1.5, 0.2], "std": [0.35, 0.38, 0.17, 0.1]},
        "versicolor": {"mean": [5.9, 2.8, 4.3, 1.3], "std": [0.52, 0.31, 0.47, 0.2]},
        "virginica":  {"mean": [6.6, 3.0, 5.6, 2.0], "std": [0.64, 0.32, 0.55, 0.27]},
    }
    
    X, y = [], []
    for cls in classes:
        params = class_params[cls]
        for _ in range(50):
            features = [random.gauss(mu, sigma) for mu, sigma in zip(params["mean"], params["std"])]
            X.append(features)
            y.append(cls)
    
    # Shuffle
    combined = list(zip(X, y))
    random.shuffle(combined)
    X, y = zip(*combined)
    X, y = list(X), list(y)
    
    # Split
    split = int(len(X) * 0.75)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    feature_names = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
    
    print(f"  Dataset: {len(X)} samples, 4 features, 3 classes")
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")
    print()
    
    # Test different max depths
    print("  Effect of max_depth on accuracy:")
    print(f"    {'Depth':>6s}  {'Train Acc':>10s}  {'Test Acc':>10s}  {'Notes':>25s}")
    print(f"    {'─'*6}  {'─'*10}  {'─'*10}  {'─'*25}")
    
    for depth in [1, 2, 3, 4, 5, 7, 10, None]:
        d = depth if depth else 99
        tree = DecisionTreeClassifier(max_depth=d)
        tree.fit(X_train, y_train)
        train_acc = tree.score(X_train, y_train)
        test_acc = tree.score(X_test, y_test)
        
        notes = ""
        if depth == 1:
            notes = "(underfitting)"
        elif depth == 3:
            notes = "(good)"
        elif depth is None:
            notes = "(overfitting!)"
        elif train_acc > 0.99 and test_acc < 0.95:
            notes = "(overfitting)"
        
        depth_str = str(depth) if depth else "None"
        print(f"    {depth_str:>6s}  {train_acc:>10.2%}  {test_acc:>10.2%}  {notes:>25s}")
    
    # Best tree
    best_tree = DecisionTreeClassifier(max_depth=4)
    best_tree.fit(X_train, y_train)
    
    print(f"\n  Best tree (max_depth=4) test accuracy: {best_tree.score(X_test, y_test):.2%}")
    best_tree.print_tree(feature_names)
    
    # Confusion analysis
    predictions = best_tree.predict(X_test)
    print("\n  Per-class accuracy:")
    for cls in classes:
        cls_indices = [i for i, label in enumerate(y_test) if label == cls]
        cls_correct = sum(1 for i in cls_indices if predictions[i] == cls)
        cls_total = len(cls_indices)
        print(f"    {cls:>12s}: {cls_correct}/{cls_total} = {cls_correct/cls_total:.0%}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    demo_entropy()
    demo_decision_tree_2d()
    demo_decision_tree_iris()
    
    print("\n" + "=" * 65)
    print("  DECISION TREE SUMMARY")
    print("=" * 65)
    print("""
  Decision trees are the most INTERPRETABLE ML algorithm:
  
  1. At each node, find the feature+threshold that maximizes
     information gain (reduces entropy the most)
  2. Split the data and recurse on each half
  3. Stop when: max depth reached, too few samples, or pure leaf
  
  Key concepts:
  - Entropy: measures impurity (0 = pure, 1 = max mixed)
  - Information gain: entropy reduction from a split
  - max_depth: primary tool to prevent overfitting
  
  Pros: Interpretable, handles non-linear data, no feature scaling needed
  Cons: Prone to overfitting, unstable (small data changes = different tree)
  
  Random Forest = many decision trees voting together. This fixes the
  overfitting and instability problems while keeping the interpretability.
""")
