"""
Episode 7 — Gradient Descent Visualized (From Scratch)
======================================================
Pure Python visualization of gradient descent on a simple function.
Shows iterations, learning rate effects, and convergence behavior.

No external dependencies. Pure Python 3 standard library only.
"""

import math
import random


# =============================================================================
# THE FUNCTION WE WANT TO MINIMIZE
# =============================================================================

def f(x):
    """Our target function: f(x) = (x - 3)^2 + 1
    
    This has a clear minimum at x=3, f(3) = 1.
    Simple parabola — easy to visualize and understand.
    """
    return (x - 3) ** 2 + 1


def df(x):
    """Derivative (gradient) of f: f'(x) = 2(x - 3)
    
    This tells us the slope at any point x.
    -> Negative slope means minimum is to the RIGHT (increase x)
    -> Positive slope means minimum is to the LEFT (decrease x)
    -> Zero slope means we're at the minimum.
    """
    return 2 * (x - 3)


def loss_function_2d(x, y):
    """A 2D loss surface for the second demo: f(x,y) = x^2 + y^2 + x*y
    
    Minimum at (0, 0). Bowl-shaped with a slight twist from the xy term.
    """
    return x ** 2 + y ** 2 + x * y


def loss_gradient_2d(x, y):
    """Gradient of the 2D loss: [df/dx, df/dy] = [2x + y, 2y + x]"""
    return [2 * x + y, 2 * y + x]


# =============================================================================
# GRADIENT DESCENT IMPLEMENTATION
# =============================================================================

def gradient_descent_1d(start_x, learning_rate, num_iterations, func, grad_func):
    """Run gradient descent in 1D and record the path.
    
    Parameters:
        start_x:        Starting point
        learning_rate:  Step size (how fast we descend)
        num_iterations: Number of steps to take
        func:           The function to minimize
        grad_func:      The derivative/gradient of the function
    
    Returns:
        path: List of (x, f(x)) tuples showing the descent path
    """
    x = start_x
    path = [(x, func(x))]
    
    for _ in range(num_iterations):
        gradient = grad_func(x)
        x = x - learning_rate * gradient
        path.append((x, func(x)))
    
    return path


def gradient_descent_2d(start_x, start_y, learning_rate, num_iterations, func, grad_func):
    """Run gradient descent in 2D and record the path."""
    x, y = start_x, start_y
    path = [(x, y, func(x, y))]
    
    for _ in range(num_iterations):
        grad_x, grad_y = grad_func(x, y)
        x = x - learning_rate * grad_x
        y = y - learning_rate * grad_y
        path.append((x, y, func(x, y)))
    
    return path


# =============================================================================
# ASCII VISUALIZATION
# =============================================================================

def ascii_plot_descent(path, func, title="Gradient Descent", width=60, height=20):
    """Create an ASCII plot of the function with the descent path overlaid.
    
    Parameters:
        path:  List of (x, f(x)) points from gradient descent
        func:  The function being minimized
        title: Plot title
        width:  Plot width in characters
        height: Plot height in characters
    """
    # Determine x range from path with some padding
    xs = [p[0] for p in path]
    x_min = min(min(xs) - 1, -1)
    x_max = max(max(xs) + 1, 5)
    
    # Sample function values
    num_samples = width
    sample_xs = [x_min + (x_max - x_min) * i / (num_samples - 1) for i in range(num_samples)]
    sample_ys = [func(x) for x in sample_xs]
    
    # Add the path y values to get full range
    all_ys = sample_ys + [p[1] for p in path]
    y_min = min(all_ys) - 0.5
    y_max = max(all_ys) + 0.5
    
    # Create the plot grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    def to_grid(x_val, y_val):
        """Convert data coordinates to grid coordinates."""
        col = int((x_val - x_min) / (x_max - x_min) * (width - 1))
        row = int((1 - (y_val - y_min) / (y_max - y_min)) * (height - 1))
        return max(0, min(height - 1, row)), max(0, min(width - 1, col))
    
    # Draw the function curve
    for i, (sx, sy) in enumerate(zip(sample_xs, sample_ys)):
        row, col = to_grid(sx, sy)
        grid[row][col] = '.'
    
    # Draw the descent path
    markers = ['o'] * len(path)
    markers[0] = 'S'  # Start
    markers[-1] = 'E'  # End
    
    for i, (px, py) in enumerate(path):
        row, col = to_grid(px, py)
        # Only draw if not overwriting the start/end markers
        if grid[row][col] in (' ', '.'):
            grid[row][col] = markers[i] if i < len(markers) else 'o'
        else:
            grid[row][col] = '*'  # Overlap point
    
    # Render
    print(f"\n  {title}")
    print(f"  {'─' * width}")
    for i, row in enumerate(grid):
        y_label = y_max - (y_max - y_min) * i / (height - 1) if i % 4 == 0 else ''
        y_label = f"{y_label:6.1f}" if y_label != '' else "      "
        print(f"  {y_label}|{''.join(row)}|")
    print(f"  {'':>6s}+{'─' * width}+")
    print(f"  {'':>7s}{x_min:.0f}{' ' * (width - 8)}{x_max:.0f}")
    
    # Legend
    print(f"\n  Legend: S = start, o = step, E = end, . = function curve")
    print(f"  Minimum is at x=3.0, f(x)=1.0")


def print_convergence_table(path, func, max_rows=15):
    """Print a table showing each step of gradient descent."""
    print(f"\n  {'Step':>4s}  {'x':>10s}  {'f(x)':>10s}  {'gradient':>10s}  {'|gradient|':>11s}")
    print(f"  {'─'*4}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*11}")
    
    for i in range(min(len(path), max_rows)):
        x, fx = path[i]
        grad = df(x)
        marker = " <-- START" if i == 0 else (" <-- CLOSE!" if abs(grad) < 0.01 else "")
        print(f"  {i:4d}  {x:10.6f}  {fx:10.6f}  {grad:10.6f}  {abs(grad):11.6f}{marker}")
    
    if len(path) > max_rows:
        print(f"  ... ({len(path) - max_rows} more steps) ...")
        x, fx = path[-1]
        grad = df(x)
        print(f"  {len(path)-1:4d}  {x:10.6f}  {fx:10.6f}  {grad:10.6f}  {abs(grad):11.6f}  <-- FINAL")


# =============================================================================
# DEMO: EFFECT OF LEARNING RATE
# =============================================================================

def demo_learning_rate_effects():
    """Show how different learning rates affect convergence."""
    print("=" * 65)
    print("  GRADIENT DESCENT: The Effect of Learning Rate")
    print("=" * 65)
    print()
    print("  Function: f(x) = (x-3)^2 + 1  (minimum at x=3)")
    print("  Starting point: x = -2.0")
    print("  Gradient: f'(x) = 2(x-3)")
    print()
    
    # Scenario 1: Small learning rate — slow but steady
    print("  ┌─────────────────────────────────────────────────────────────┐")
    print("  │ SCENARIO 1: Learning Rate = 0.01 (too small)              │")
    print("  │ Takes many steps to converge. Safe but slow.               │")
    print("  └─────────────────────────────────────────────────────────────┘")
    
    path_small = gradient_descent_1d(
        start_x=-2.0, learning_rate=0.01, num_iterations=50,
        func=f, grad_func=df
    )
    ascii_plot_descent(path_small, f, "lr=0.01 (too small, needs 200+ steps)", width=60, height=12)
    print_convergence_table(path_small[:8], f)
    print(f"\n  After 50 steps: x={path_small[-1][0]:.4f}, f(x)={path_small[-1][1]:.4f}")
    print(f"  Still far from minimum x=3.0! Needs more iterations.")
    
    # Scenario 2: Good learning rate — converges nicely
    print("\n\n  ┌─────────────────────────────────────────────────────────────┐")
    print("  │ SCENARIO 2: Learning Rate = 0.3 (just right!)              │")
    print("  │ Smooth convergence. Reaches minimum in ~15-20 steps.       │")
    print("  └─────────────────────────────────────────────────────────────┘")
    
    path_good = gradient_descent_1d(
        start_x=-2.0, learning_rate=0.3, num_iterations=30,
        func=f, grad_func=df
    )
    ascii_plot_descent(path_good, f, "lr=0.3 (good convergence)", width=60, height=12)
    print_convergence_table(path_good, f)
    print(f"\n  After 30 steps: x={path_good[-1][0]:.6f}, f(x)={path_good[-1][1]:.6f}")
    print(f"  Converged to near-minimum!")
    
    # Scenario 3: Large learning rate — oscillates
    print("\n\n  ┌─────────────────────────────────────────────────────────────┐")
    print("  │ SCENARIO 3: Learning Rate = 0.8 (too large, oscillates)   │")
    print("  │ Overshoots back and forth, may never converge.             │")
    print("  └─────────────────────────────────────────────────────────────┘")
    
    path_large = gradient_descent_1d(
        start_x=-2.0, learning_rate=0.8, num_iterations=15,
        func=f, grad_func=df
    )
    ascii_plot_descent(path_large, f, "lr=0.8 (oscillation!)", width=60, height=12)
    print_convergence_table(path_large, f)
    print(f"\n  Notice: x jumps back and forth across the minimum!")
    print(f"  After 15 steps: x={path_large[-1][0]:.4f} — oscillating, not converging.")
    
    # Scenario 4: Way too large — diverges
    print("\n\n  ┌─────────────────────────────────────────────────────────────┐")
    print("  │ SCENARIO 4: Learning Rate = 1.5 (DIVERGES!)               │")
    print("  │ Each step makes things WORSE. Gradient explodes.           │")
    print("  └─────────────────────────────────────────────────────────────┘")
    
    path_diverge = gradient_descent_1d(
        start_x=-2.0, learning_rate=1.5, num_iterations=8,
        func=f, grad_func=df
    )
    print(f"\n  {'Step':>4s}  {'x':>10s}  {'f(x)':>10s}")
    print(f"  {'─'*4}  {'─'*10}  {'─'*10}")
    for i, (x, fx) in enumerate(path_diverge):
        print(f"  {i:4d}  {x:10.4f}  {fx:10.4f}")
    print(f"\n  ERROR: Loss is INCREASING! The algorithm diverged.")
    print(f"  This is why learning rate matters so much in practice.")


def demo_2d_gradient_descent():
    """Show gradient descent in 2D — more realistic."""
    print("\n\n" + "=" * 65)
    print("  2D GRADIENT DESCENT: Minimizing f(x,y) = x^2 + y^2 + x*y")
    print("=" * 65)
    print()
    print("  This is what loss surfaces look like in real ML (simplified).")
    print("  Each step adjusts MULTIPLE parameters simultaneously.")
    print()
    
    random.seed(7)
    start_x, start_y = 4.0, -3.0
    
    path = gradient_descent_2d(
        start_x=start_x, start_y=start_y,
        learning_rate=0.15, num_iterations=25,
        func=loss_function_2d, grad_func=loss_gradient_2d
    )
    
    print(f"  Starting at ({start_x}, {start_y}), loss = {path[0][2]:.4f}")
    print(f"  Target: (0, 0), loss = 0.0")
    print()
    print(f"  {'Step':>4s}  {'x':>8s}  {'y':>8s}  {'loss':>10s}  {'progress':>20s}")
    print(f"  {'─'*4}  {'─'*8}  {'─'*8}  {'─'*10}  {'─'*20}")
    
    initial_loss = path[0][2]
    for i, (x, y, loss) in enumerate(path):
        progress = 1.0 - (loss / initial_loss) if initial_loss != 0 else 1.0
        bar = "#" * int(progress * 20)
        if i % 3 == 0 or i == len(path) - 1:
            print(f"  {i:4d}  {x:8.4f}  {y:8.4f}  {loss:10.4f}  [{bar:<20s}] {progress*100:.1f}%")
    
    final = path[-1]
    print(f"\n  Final: x={final[0]:.6f}, y={final[1]:.6f}, loss={final[2]:.6f}")
    print(f"  Reduced loss from {initial_loss:.4f} to {final[2]:.6f}")
    print(f"  This is exactly how neural networks learn — just with millions of parameters.")


def demo_concept_explainer():
    """Explain the core concepts clearly."""
    print("\n\n" + "=" * 65)
    print("  KEY CONCEPTS RECAP")
    print("=" * 65)
    print("""
  DERIVATIVE = slope of a function at a point
  -> f(x) = x^2,  f'(x) = 2x
  -> At x=2, slope = 4 (going up fast)
  -> At x=-1, slope = -2 (going down)
  -> At x=0, slope = 0 (flat, this is the minimum or maximum)

  GRADIENT = vector of partial derivatives (one per parameter)
  -> Points in direction of STEEPEST ASCENT
  -> To MINIMIZE, go the OPPOSITE direction

  GRADIENT DESCENT ALGORITHM:
  1. Start at some parameter values
  2. Compute the gradient (which way is "up hill"?)
  3. Take a step DOWN hill:  params = params - lr * gradient
  4. Repeat until the gradient is ~0 (at the bottom)

  LEARNING RATE = how big of a step you take
  -> Too big: you jump over the minimum and never land
  -> Too small: you inch forward and it takes forever
  -> Just right: you converge efficiently

  In a neural network:
  -> The function is the LOSS (how wrong are we?)
  -> The parameters are all the WEIGHTS and BIASES
  -> Gradient descent adjusts all of them simultaneously
  -> Backpropagation is just the chain rule (calculus) computing each gradient

  That's it. That's how AI learns.
""")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    demo_learning_rate_effects()
    demo_2d_gradient_descent()
    demo_concept_explainer()
