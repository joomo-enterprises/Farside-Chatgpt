"""
Episode 7 — Linear Algebra for AI (From Scratch)
=================================================
Implements core linear algebra operations without NumPy:
  - Vector operations: dot product, addition, scalar multiplication
  - Matrix operations: multiplication, transpose
  - Neural network connection: single neuron and a full layer
  
No external dependencies. Pure Python 3 standard library only.
"""

import math
import random


# =============================================================================
# VECTOR OPERATIONS
# =============================================================================

def vector_dot(a, b):
    """Compute the dot product of two vectors.
    
    The dot product measures similarity between vectors.
    Large positive = similar direction, ~0 = orthogonal, negative = opposite.
    This is the fundamental operation inside every neuron.
    """
    if len(a) != len(b):
        raise ValueError(f"Vectors must be same length: {len(a)} vs {len(b)}")
    return sum(ai * bi for ai, bi in zip(a, b))


def vector_add(a, b):
    """Element-wise vector addition."""
    if len(a) != len(b):
        raise ValueError(f"Vectors must be same length: {len(a)} vs {len(b)}")
    return [ai + bi for ai, bi in zip(a, b)]


def vector_scale(v, scalar):
    """Multiply every element of a vector by a scalar."""
    return [vi * scalar for vi in v]


def vector_magnitude(v):
    """Compute the Euclidean length (L2 norm) of a vector."""
    return math.sqrt(sum(vi ** 2 for vi in v))


def vector_cosine_similarity(a, b):
    """Cosine similarity = dot product of normalized vectors.
    
    Returns a value between -1 and 1. This is what search engines
    and embedding models use to find similar items.
    """
    mag_a = vector_magnitude(a)
    mag_b = vector_magnitude(b)
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return vector_dot(a, b) / (mag_a * mag_b)


# =============================================================================
# MATRIX OPERATIONS
# =============================================================================

def matrix_shape(matrix):
    """Return (rows, cols) of a matrix."""
    if not matrix:
        return (0, 0)
    return (len(matrix), len(matrix[0]))


def matrix_transpose(matrix):
    """Transpose a matrix: swap rows and columns."""
    rows, cols = matrix_shape(matrix)
    return [[matrix[r][c] for r in range(rows)] for c in range(cols)]


def matrix_multiply(A, B):
    """Multiply matrix A by matrix B.
    
    This is equivalent to computing dot products between rows of A
    and columns of B. THIS is what a neural network layer does.
    
    A: (m, n), B: (n, p) -> result: (m, p)
    """
    rows_a, cols_a = matrix_shape(A)
    rows_b, cols_b = matrix_shape(B)
    
    if cols_a != rows_b:
        raise ValueError(
            f"Cannot multiply: A is {rows_a}x{cols_a}, B is {rows_b}x{cols_b} "
            f"(A's columns must equal B's rows)"
        )
    
    # Transpose B so we can use our dot product on rows
    B_T = matrix_transpose(B)
    result = []
    for row_a in A:
        result_row = []
        for col_b in B_T:
            result_row.append(vector_dot(row_a, col_b))
        result.append(result_row)
    return result


def matrix_vector_multiply(matrix, vector):
    """Multiply a matrix by a vector: apply dot product with each row."""
    return [vector_dot(row, vector) for row in matrix]


# =============================================================================
# NEURAL NETWORK CONNECTION
# =============================================================================

def sigmoid(x):
    """Sigmoid activation function: squashes any value to range (0, 1)."""
    return 1.0 / (1.0 + math.exp(-max(-500, min(500, x))))  # clamp for stability


def relu(x):
    """ReLU activation function: max(0, x). The most popular activation."""
    return max(0, x)


def single_neuron(inputs, weights, bias, activation='sigmoid'):
    """A single artificial neuron.
    
    Inputs:  x1, x2, x3, ... (the data or previous layer output)
    Weights: w1, w2, w3, ... (learned parameters)
    Bias:    b (learned offset)
    
    output = activation(dot(inputs, weights) + bias)
    
    This is AI's equivalent of a transistor — billions of these
    make up modern neural networks.
    """
    if activation == 'sigmoid':
        return sigmoid(vector_dot(inputs, weights) + bias)
    elif activation == 'relu':
        return relu(vector_dot(inputs, weights) + bias)
    else:
        raise ValueError(f"Unknown activation: {activation}")


def dense_layer(inputs, weights_matrix, biases, activation='sigmoid'):
    """A fully-connected (dense) neural network layer.
    
    weights_matrix: each row is one neuron's weights
    biases: one bias per neuron
    
    output[i] = activation(dot(inputs, weights[i]) + biases[i])
    
    This is the core operation of every neural network.
    """
    outputs = []
    for neuron_weights, bias in zip(weights_matrix, biases):
        outputs.append(single_neuron(inputs, neuron_weights, bias, activation))
    return outputs


def random_matrix(rows, cols, scale=0.5):
    """Create a matrix with small random values."""
    return [[random.uniform(-scale, scale) for _ in range(cols)] for _ in range(rows)]


def random_vector(length, scale=0.5):
    """Create a vector with small random values."""
    return [random.uniform(-scale, scale) for _ in range(length)]


# =============================================================================
# DEMO: HOW LINEAR ALGEBRA POWERS A NEURAL NETWORK
# =============================================================================

def demo_linear_algebra_basics():
    print("=" * 65)
    print("  LINEAR ALGEBRA BASICS FOR AI")
    print("=" * 65)
    
    print("\n--- DOT PRODUCT (Measures Similarity) ---")
    a = [1.0, 2.0, 3.0]
    b = [4.0, 5.0, 6.0]
    print(f"  vector a = {a}")
    print(f"  vector b = {b}")
    print(f"  dot(a, b) = {vector_dot(a, b):.2f}")
    print(f"  cosine_similarity(a, b) = {vector_cosine_similarity(a, b):.4f}")
    
    # Show orthogonal vectors
    x = [1.0, 0.0, 0.0]
    y = [0.0, 1.0, 0.0]
    print(f"\n  Orthogonal vectors: dot({x}, {y}) = {vector_dot(x, y):.1f} (no relationship)")
    
    # Show opposite vectors
    fwd = [1.0, 2.0, 3.0]
    back = [-1.0, -2.0, -3.0]
    print(f"  Opposite vectors: dot({fwd}, {back}) = {vector_dot(fwd, back):.2f} (opposite)")
    
    print("\n--- MATRIX MULTIPLICATION ---")
    A = [[1, 2], [3, 4], [5, 6]]  # 3x2
    B = [[7, 8, 9], [10, 11, 12]]  # 2x3
    result = matrix_multiply(A, B)  # 3x3
    print(f"  A (3x2): {A}")
    print(f"  B (2x3): {B}")
    print(f"  A @ B (3x3): {result}")
    
    print("\n--- MATRIX * VECTOR (Neural Network Layer) ---")
    inputs = [0.5, 0.3]  # 2 inputs
    weights = [
        [0.1, 0.2],  # neuron 1 weights
        [0.3, 0.5],  # neuron 2 weights
        [0.7, 0.1],  # neuron 3 weights
    ]  # 3 neurons, each with 2 weights
    output = matrix_vector_multiply(weights, inputs)
    print(f"  Input vector: {inputs} (length {len(inputs)})")
    print(f"  Weight matrix: {len(weights)}x{len(weights[0])} (3 neurons, 2 inputs each)")
    print(f"  Output: {[f'{v:.4f}' for v in output]} (length {len(output)})")
    print(f"  -> 2 inputs became 3 outputs via matrix-vector multiplication")


def demo_neural_network():
    print("\n" + "=" * 65)
    print("  NEURAL NETWORK DEMO: 2-Layer Forward Pass")
    print("=" * 65)
    
    random.seed(42)
    
    # Simulating a simple problem: 3 binary features -> 2 hidden neurons -> 1 output
    # Like classifying: "Is this email spam?" based on 3 features
    
    print("\n  Architecture: 3 inputs -> 2 hidden -> 1 output")
    print("  " + "-" * 40)
    
    # Input: [has_keyword, has_link, has_attachment]
    email_features = [1.0, 0.5, 0.0]
    print(f"\n  Input features: {email_features}")
    print("  (has_keyword=1.0, has_link=0.5, has_attachment=0.0)")
    
    # Hidden layer: 3 inputs -> 2 neurons
    hidden_weights = random_matrix(2, 3, scale=1.0)
    hidden_biases = random_vector(2, scale=0.1)
    hidden_output = dense_layer(email_features, hidden_weights, hidden_biases, 'sigmoid')
    print(f"\n  Hidden layer (3 -> 2, sigmoid):")
    print(f"    Weights: {[[f'{w:.3f}' for w in row] for row in hidden_weights]}")
    print(f"    Biases:  {[f'{b:.3f}' for b in hidden_biases]}")
    print(f"    Output:  {[f'{v:.4f}' for v in hidden_output]}")
    
    # Output layer: 2 hidden -> 1 output
    output_weights = random_matrix(1, 2, scale=1.0)
    output_biases = random_vector(1, scale=0.1)
    final_output = dense_layer(hidden_output, output_weights, output_biases, 'sigmoid')
    print(f"\n  Output layer (2 -> 1, sigmoid):")
    print(f"    Weights: {[[f'{w:.3f}' for w in row] for row in output_weights]}")
    print(f"    Biases:  {[f'{b:.3f}' for b in output_biases]}")
    print(f"    Output:  {final_output[0]:.4f}")
    print(f"    -> Probability of spam: {final_output[0]*100:.1f}%")
    
    print("\n  WHAT JUST HAPPENED?")
    print("  1. Input vector (1x3) was multiplied through hidden weight matrix (2x3)")
    print("  2. Sigmoid activation applied element-wise: non-linearity!")
    print("  3. Hidden output (1x2) was multiplied through output weights (1x2)")
    print("  4. Final sigmoid: probability between 0 and 1")
    print("  That's a forward pass through a neural network.")
    print("  Training this = adjusting all those weights and biases via gradient descent.")


def demo_embedding_similarity():
    print("\n" + "=" * 65)
    print("  WORD EMBEDDINGS: Finding Similar Words (From Scratch)")
    print("=" * 65)
    
    # Tiny fake embeddings (normally 100-300 dimensions, using 4 for demo)
    # Imagine these are Word2Vec-style vectors
    embeddings = {
        "king":   [0.8, 0.6, 0.3, 0.1],
        "queen":  [0.7, 0.9, 0.3, 0.2],
        "man":    [0.9, 0.2, 0.4, 0.1],
        "woman":  [0.6, 0.8, 0.4, 0.3],
        "apple":  [0.1, 0.2, 0.9, 0.8],
        "orange": [0.2, 0.3, 0.8, 0.7],
        "car":    [0.3, 0.1, 0.2, 0.9],
    }
    
    print("\n  Words and their 4-dim embedding vectors:")
    for word, vec in embeddings.items():
        print(f"    {word:>8s} -> {vec}")
    
    print("\n  Cosine similarities (higher = more similar):")
    words = list(embeddings.keys())
    pairs = []
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            sim = vector_cosine_similarity(embeddings[words[i]], embeddings[words[j]])
            pairs.append((words[i], words[j], sim))
    
    # Sort by similarity descending
    pairs.sort(key=lambda x: x[2], reverse=True)
    
    for w1, w2, sim in pairs:
        bar = "#" * int(abs(sim) * 30)
        label = "SIMILAR" if sim > 0.8 else ("neutral" if sim > 0.3 else "different")
        print(f"    {w1:>8s} vs {w2:<8s} : {sim:+.4f} |{bar}| {label}")
    
    print("\n  KEY INSIGHT: 'king' and 'queen' are most similar among the pairs")
    print("  'apple' and 'orange' cluster together. 'car' is distant from fruits.")
    print("  This is how AI understands semantic relationships via vector math.")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    demo_linear_algebra_basics()
    demo_neural_network()
    demo_embedding_similarity()
    
    print("\n" + "=" * 65)
    print("  SUMMARY: The 3 Operations That Power AI")
    print("=" * 65)
    print("""
  1. DOT PRODUCT  — measures similarity (used in attention, embeddings)
  2. MATRIX MULTIPLY — transforms data between neural network layers
  3. ACTIVATION FUNCTION — adds non-linearity (sigmoid, ReLU)
  
  Every neural network = stacks of matrix multiplies + non-linearities.
  Training = computing gradients to adjust all the weights and biases.
  
  That's the linear algebra behind AI.
""")
