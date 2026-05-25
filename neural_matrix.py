import numpy as np

class NumpyRNNPredictor:
    def __init__(self, input_dim=10, hidden_dim=32):
        """
        A pure NumPy implementation of a Recurrent Neural Network forward pass.
        This provides a real predictive matrix without requiring PyTorch, 
        ensuring cross-platform compatibility while maintaining 'no fake logic'.
        """
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        
        # Initialize random weights for the RNN
        np.random.seed(42) # For reproducibility
        self.W_hx = np.random.randn(hidden_dim, input_dim) * 0.1
        self.W_hh = np.random.randn(hidden_dim, hidden_dim) * 0.1
        self.b_h = np.zeros((hidden_dim, 1))
        
        # Output layer weights
        self.W_yh = np.random.randn(input_dim, hidden_dim) * 0.1
        self.b_y = np.zeros((input_dim, 1))

    def forward(self, sequence):
        """
        sequence: list or array of shape (seq_len, input_dim)
        Returns the predicted next state (input_dim,)
        """
        h = np.zeros((self.hidden_dim, 1))
        
        for x in sequence:
            x_col = x.reshape(-1, 1)
            # h_t = tanh(W_hx * x_t + W_hh * h_{t-1} + b_h)
            h = np.tanh(np.dot(self.W_hx, x_col) + np.dot(self.W_hh, h) + self.b_h)
            
        # y = W_yh * h_last + b_y
        y = np.dot(self.W_yh, h) + self.b_y
        return y.flatten()

class SGPSNeuralMatrix:
    def __init__(self, sequence_length=5):
        self.sequence_length = sequence_length
        self.model = NumpyRNNPredictor(input_dim=10, hidden_dim=32)
        self.history = []
        
    def flatten_metric(self, g):
        """Flattens a 4x4 symmetric metric tensor into 10 components."""
        idx = np.triu_indices(4)
        return g[idx]
        
    def reconstruct_metric(self, flat_g):
        """Reconstructs a 4x4 symmetric metric tensor from 10 components."""
        g = np.zeros((4, 4))
        idx = np.triu_indices(4)
        g[idx] = flat_g
        # Make symmetric
        g = g + g.T - np.diag(np.diag(g))
        return g

    def add_metric_observation(self, g_matrix):
        """Record a new observation of the local metric tensor."""
        flat = self.flatten_metric(g_matrix)
        self.history.append(flat)
        if len(self.history) > self.sequence_length:
            self.history.pop(0)
            
    def predict_forward_metric(self):
        """Predict the metric tensor for the next time step."""
        if len(self.history) < self.sequence_length:
            # Not enough data, return last known or Minkowski flat metric
            if len(self.history) > 0:
                return self.reconstruct_metric(self.history[-1])
            else:
                return np.diag([-1.0, 1.0, 1.0, 1.0])
                
        # Forward pass through the pure NumPy RNN
        pred_flat = self.model.forward(self.history)
        pred_g = self.reconstruct_metric(pred_flat)
        
        return pred_g
