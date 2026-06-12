"""
Episode 8 — Linear Regression From Scratch
===========================================
Linear regression using gradient descent with ASCII visualization.
Pure Python — no NumPy, no scikit-learn.

Finds the best-fit line y = wx + b by minimizing mean squared error.
"""

import math
import random


# =============================================================================
# LINEAR REGRESSION MODEL
# =============================================================================

class LinearRegression:
    """Linear regression using gradient descent.
    
    Model: y = w * x + b
    Loss:  MSE = mean((y_pred - y_actual)^2)
    
    Parameters:
        learning_rate: Step size for gradient descent
        n_iterations:  Number of training steps
    """
    
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        self.lr = learning_rate
        self.n_iter = n_iterations
        self.w = 0.0  # slope
        self.b = 0.0  # intercept
        self.loss_history = []
    
    def predict(self, x):
        """Predict y for a single x value."""
        return self.w * x + self.b
    
    def predict_batch(self, X):
        """Predict y for multiple x values."""
        return [self.predict(x) for x in X]
    
    def mse(self, X, y):
        """Compute mean squared error."""
        predictions = self.predict_batch(X)
        return sum((pred - actual) ** 2 for pred, actual in zip(predictions, y)) / len(X)
    
    def _compute_gradients(self, X, y):
        """Compute gradients of MSE with respect to w and b.
        
        d(MSE)/dw = (2/n) * sum((y_pred - y) * x)
        d(MSE)/db = (2/n) * sum(y_pred - y)
        
        These tell us which direction to adjust w and b to reduce error.
        """
        n = len(X)
        predictions = self.predict_batch(X)
        
        dw = 0.0
        db = 0.0
        for xi, yi, pred in zip(X, y, predictions):
            error = pred - yi
            dw += error * xi
            db += error
        
        dw = (2.0 / n) * dw
        db = (2.0 / n) * db
        
        return dw, db
    
    def fit(self, X, y, verbose=False):
        """Train the model using gradient descent."""
        self.loss_history = []
        self.w = 0.0
        self.b = 0.0
        
        for i in range(self.n_iter):
            # Compute loss
            loss = self.mse(X, y)
            self.loss_history.append(loss)
            
            # Compute gradients
            dw, db = self._compute_gradients(X, y)
            
            # Update parameters
            self.w -= self.lr * dw
            self.b -= self.lr * db
            
            if verbose and (i % (self.n_iter // 10) == 0 or i == self.n_iter - 1):
                print(f"    Iteration {i:5d}: loss={loss:.6f}, w={self.w:.4f}, b={self.b:.4f}")
        
        return self
    
    def r_squared(self, X, y):
        """Compute R² (coefficient of determination).
        
        R² = 1 - (SS_res / SS_tot)
        - 1.0 = perfect fit
        - 0.0 = no better than predicting the mean
        - < 0 = worse than predicting the mean
        """
        predictions = self.predict_batch(X)
        y_mean = sum(y) / len(y)
        
        ss_res = sum((yi - pred) ** 2 for yi, pred in zip(y, predictions))
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        
        if ss_tot == 0:
            return 1.0
        return 1.0 - (ss_res / ss_tot)
    
    def score(self, X, y):
        """R² score (alias for scikit-learn compatibility)."""
        return self.r_squared(X, y)


# =============================================================================
# ASCII VISUALIZATION
# =============================================================================

def ascii_scatter_with_line(X, y, model, title="Linear Regression", width=60, height=20):
    """Create an ASCII scatter plot with the regression line.
    
    Parameters:
        X, y:   Data points
        model:  Trained LinearRegression model
        title:  Plot title
        width:  Plot width in characters
        height: Plot height in characters
    """
    if not X:
        return
    
    # Determine plot bounds
    x_min, x_max = min(X), max(X)
    y_min, y_max = min(y), max(y)
    
    # Add padding
    x_pad = (x_max - x_min) * 0.1 or 1
    y_pad = (y_max - y_min) * 0.1 or 1
    x_min -= x_pad
    x_max += x_pad
    y_min -= y_pad
    y_max += y_pad
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    def to_grid(x_val, y_val):
        col = int((x_val - x_min) / (x_max - x_min) * (width - 1))
        row = int((1 - (y_val - y_min) / (y_max - y_min)) * (height - 1))
        return max(0, min(height - 1, row)), max(0, min(width - 1, col))
    
    # Draw regression line
    for col in range(width):
        x_val = x_min + (x_max - x_min) * col / (width - 1)
        y_val = model.predict(x_val)
        if y_min <= y_val <= y_max:
            row, c = to_grid(x_val, y_val)
            if grid[row][c] == ' ':
                grid[row][c] = '-'
    
    # Draw data points
    for xi, yi in zip(X, y):
        row, col = to_grid(xi, yi)
        grid[row][col] = 'o'
    
    # Render
    print(f"\n  {title}")
    print(f"  y = {model.w:.4f} * x + {model.b:.4f}")
    print(f"  {'─' * width}")
    
    for i, row in enumerate(grid):
        y_label = y_max - (y_max - y_min) * i / (height - 1) if i % 4 == 0 else ''
        y_label = f"{y_label:6.1f}" if y_label != '' else "      "
        print(f"  {y_label}|{''.join(row)}|")
    
    print(f"  {'':>6s}+{'─' * width}+")
    print(f"  {'':>7s}{x_min:.1f}{' ' * (width - 8)}{x_max:.1f}")
    print(f"\n  Legend: o = data point, - = regression line")


def ascii_loss_curve(loss_history, width=50, height=12):
    """Plot the training loss over iterations."""
    if not loss_history:
        return
    
    # Sample if too many iterations
    if len(loss_history) > width:
        step = len(loss_history) // width
        sampled = [loss_history[i] for i in range(0, len(loss_history), step)]
    else:
        sampled = loss_history
    
    loss_min = min(sampled)
    loss_max = max(sampled)
    
    if loss_max == loss_min:
        loss_max = loss_min + 1
    
    grid = [[' ' for _ in range(len(sampled))] for _ in range(height)]
    
    for col, loss in enumerate(sampled):
        row = int((1 - (loss - loss_min) / (loss_max - loss_min)) * (height - 1))
        row = max(0, min(height - 1, row))
        grid[row][col] = '#'
    
    print(f"\n  Training Loss Over Iterations")
    print(f"  {'─' * len(sampled)}")
    for i, row in enumerate(grid):
        y_label = loss_max - (loss_max - loss_min) * i / (height - 1) if i % 3 == 0 else ''
        y_label = f"{y_label:6.2f}" if y_label != '' else "      "
        print(f"  {y_label}|{''.join(row)}|")
    print(f"  {'':>6s}+{'─' * len(sampled)}+")
    print(f"  {'':>7s}0{' ' * (len(sampled) - 6)}{len(loss_history)} iterations")


# =============================================================================
# DEMO
# =============================================================================

def demo_simple_regression():
    """Basic linear regression demo."""
    print("=" * 65)
    print("  LINEAR REGRESSION: Simple Demo")
    print("=" * 65)
    print()
    
    # Simple data: y ≈ 2x + 1 with some noise
    random.seed(42)
    X = [i * 0.5 for i in range(20)]
    y = [2.0 * x + 1.0 + random.gauss(0, 0.5) for x in X]
    
    print("  Data: y ≈ 2x + 1 (with noise)")
    print(f"  {len(X)} data points")
    print()
    
    # Train model (use smaller lr since x values go up to 9.5)
    model = LinearRegression(learning_rate=0.01, n_iterations=1000)
    print("  Training with gradient descent:")
    model.fit(X, y, verbose=True)
    
    print(f"\n  Results:")
    print(f"    Learned: y = {model.w:.4f} * x + {model.b:.4f}")
    print(f"    True:    y = 2.0000 * x + 1.0000")
    print(f"    R² score: {model.r_squared(X, y):.4f}")
    print(f"    Final MSE: {model.mse(X, y):.6f}")
    
    # Visualize
    ascii_scatter_with_line(X, y, model, "y = {:.2f}x + {:.2f}".format(model.w, model.b))
    ascii_loss_curve(model.loss_history)


def demo_learning_rate_comparison():
    """Show effect of different learning rates."""
    print("\n\n" + "=" * 65)
    print("  LEARNING RATE COMPARISON")
    print("=" * 65)
    print()
    
    random.seed(7)
    X = [i * 0.3 for i in range(30)]
    y = [1.5 * x + 0.5 + random.gauss(0, 0.3) for x in X]
    
    learning_rates = [0.001, 0.005, 0.01, 0.02]
    
    for lr in learning_rates:
        model = LinearRegression(learning_rate=lr, n_iterations=300)
        model.fit(X, y)
        r2 = model.r_squared(X, y)
        final_loss = model.loss_history[-1]
        
        print(f"  lr={lr:.3f}: w={model.w:.4f}, b={model.b:.4f}, R²={r2:.4f}, loss={final_loss:.6f}")
        
        # Mini loss curve
        sampled = model.loss_history[::30]
        max_loss = max(sampled) if sampled else 1
        bar = "".join("#" if l / max_loss > 0.5 else "." for l in sampled)
        print(f"          loss: |{bar}|")
    
    print()
    print("  Too small (0.001): slow convergence, needs more iterations")
    print("  Just right (0.05): fast convergence, good results")
    print("  Too large (>0.15): may oscillate or diverge")


def demo_real_world_scenario():
    """Regression on a realistic scenario."""
    print("\n\n" + "=" * 65)
    print("  REAL-WORLD SCENARIO: House Price Prediction")
    print("=" * 65)
    print()
    print("  Predict house price based on square footage.")
    print("  (Synthetic but realistic data)")
    print()
    
    random.seed(123)
    
    # Square feet -> price (in $1000s)
    # Realistic: ~$200/sqft with variation
    sqft = [800, 950, 1100, 1200, 1350, 1500, 1650, 1800, 1950, 2100,
            2250, 2400, 2500, 2700, 2900, 3100, 3300, 3500, 3700, 4000]
    price = [0.18 * s + random.gauss(0, 30) + 20 for s in sqft]
    
    # Normalize for better gradient descent
    x_mean = sum(sqft) / len(sqft)
    x_std = math.sqrt(sum((x - x_mean) ** 2 for x in sqft) / len(sqft))
    y_mean = sum(price) / len(price)
    y_std = math.sqrt(sum((y - y_mean) ** 2 for y in price) / len(price))
    
    X_norm = [(x - x_mean) / x_std for x in sqft]
    y_norm = [(y - y_mean) / y_std for y in price]
    
    # Train on normalized data
    model = LinearRegression(learning_rate=0.1, n_iterations=1000)
    model.fit(X_norm, y_norm, verbose=True)
    
    # Convert back to original scale
    w_original = model.w * y_std / x_std
    b_original = y_mean + model.b * y_std - w_original * x_mean
    
    print(f"\n  Original scale: price = {w_original:.4f} * sqft + {b_original:.2f}")
    print(f"  (≈ ${w_original*1000:.0f} per sqft + ${b_original*1000:.0f} base)")
    
    # Predictions
    print(f"\n  {'Sq Ft':>8s}  {'Actual ($K)':>12s}  {'Predicted ($K)':>14s}  {'Error ($K)':>12s}")
    print(f"  {'─'*8}  {'─'*12}  {'─'*14}  {'─'*12}")
    
    for i in range(len(sqft)):
        pred_norm = model.predict(X_norm[i])
        pred_original = pred_norm * y_std + y_mean
        error = price[i] - pred_original
        print(f"  {sqft[i]:>8d}  {price[i]:>12.1f}  {pred_original:>14.1f}  {error:>12.1f}")
    
    # R² on original scale
    predictions = [model.predict(X_norm[i]) * y_std + y_mean for i in range(len(sqft))]
    ss_res = sum((y_i - p_i) ** 2 for y_i, p_i in zip(price, predictions))
    ss_tot = sum((y_i - y_mean) ** 2 for y_i in price)
    r2 = 1 - ss_res / ss_tot
    
    print(f"\n  R² = {r2:.4f} ({r2*100:.1f}% of variance explained)")
    
    # Visualize (using normalized data)
    ascii_scatter_with_line(
        X_norm, y_norm, model,
        "Normalized: price = {:.3f} * sqft + {:.3f}".format(model.w, model.b)
    )


def demo_polynomial_features():
    """Show how to extend linear regression with feature engineering."""
    print("\n\n" + "=" * 65)
    print("  BEYOND LINEAR: Feature Engineering")
    print("=" * 65)
    print()
    print("  Linear regression can fit non-linear relationships")
    print("  by adding polynomial features!")
    print()
    
    random.seed(99)
    
    # Quadratic data: y = x^2 (parabola)
    X = [i * 0.2 - 2.0 for i in range(20)]
    y = [x ** 2 + random.gauss(0, 0.3) for x in X]
    
    # Add x^2 as a feature
    X_squared = [x ** 2 for x in X]
    
    # Simple approach: just regress on x^2
    model = LinearRegression(learning_rate=0.1, n_iterations=500)
    model.fit(X_squared, y, verbose=False)
    
    print("  Data: y ≈ x² (quadratic)")
    print(f"  Trained on x² as single feature:")
    print(f"    y = {model.w:.4f} * x² + {model.b:.4f}")
    print(f"    (Expected: y = 1.0 * x² + 0.0)")
    print(f"    R² = {model.r_squared(X_squared, y):.4f}")
    
    print()
    print("  KEY INSIGHT: Linear regression is 'linear' in the PARAMETERS,")
    print("  not in the FEATURES. By adding x², x³, etc. as features,")
    print("  you can fit polynomial relationships with the same algorithm!")
    print()
    print("  This is the foundation of feature engineering — the art of")
    print("  transforming raw data into features that make the problem")
    print("  linearly separable / linearly predictable.")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    demo_simple_regression()
    demo_learning_rate_comparison()
    demo_real_world_scenario()
    demo_polynomial_features()
    
    print("\n" + "=" * 65)
    print("  LINEAR REGRESSION SUMMARY")
    print("=" * 65)
    print("""
  Linear regression is the foundation of predictive modeling:
  
  1. Model: y = wx + b (a straight line)
  2. Loss: MSE = average of squared errors
  3. Training: gradient descent adjusts w and b to minimize MSE
  
  Key concepts:
  - Gradient descent: iteratively adjust parameters in the direction
    that reduces error
  - Learning rate: controls step size (too big = diverge, too small = slow)
  - R² score: fraction of variance explained (1.0 = perfect)
  - Feature engineering: add polynomial features for non-linear fits
  
  Despite its simplicity, linear regression is used everywhere:
  - Economics, finance, science, medicine, business
  - As a baseline before trying more complex models
  - As a building block inside more complex algorithms
  
  Neural networks are literally stacks of linear regressions
  with non-linear activations. Master this first.
""")
