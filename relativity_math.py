import numpy as np

class SpacetimeMetric:
    def __init__(self, metric_function, dim=4):
        """
        metric_function: a callable that takes a position vector x (shape: (dim,)) 
                         and returns the metric tensor g_mu_nu (shape: (dim, dim)).
        """
        self.metric_function = metric_function
        self.dim = dim

    def g(self, x):
        """Get the covariant metric tensor at spacetime position x."""
        g_base = self.metric_function(x)
        
        # Apply engineering biases if they exist
        if hasattr(self, 'engineering_bias'):
            for bias in self.engineering_bias:
                # Apply only in the immediate local vicinity
                dist = np.linalg.norm(x[1:] - bias['origin'][1:])
                attenuation = np.exp(-dist**2)
                g_base += bias['delta_g'] * attenuation
                
        return g_base

    def g_inv(self, x):
        """Get the contravariant (inverse) metric tensor at position x."""
        g_cov = self.g(x)
        return np.linalg.inv(g_cov)

    def partial_derivatives(self, x, epsilon=1e-6):
        """
        Computes the partial derivatives of the metric tensor using dynamic step scaling
        to prevent floating-point truncation noise at macroscopic coordinates.
        """
        partials = np.zeros((self.dim, self.dim, self.dim))
        for rho in range(self.dim):
            # Dynamic delta step based on magnitude of position coordinate
            delta = epsilon * max(1.0, abs(x[rho]))
            
            x_plus = np.copy(x)
            x_plus[rho] += delta
            g_plus = self.g(x_plus)
            
            x_minus = np.copy(x)
            x_minus[rho] -= delta
            g_minus = self.g(x_minus)
            
            partials[rho, :, :] = (g_plus - g_minus) / (2 * delta)
        return partials

    def christoffel_symbols(self, x):
        partials = self.partial_derivatives(x)
        g_contravariant = self.g_inv(x)
        gamma = np.zeros((self.dim, self.dim, self.dim))
        
        for mu in range(self.dim):
            for alpha in range(self.dim):
                for beta in range(self.dim):
                    sum_term = 0.0
                    for rho in range(self.dim):
                        term1 = partials[alpha, beta, rho]
                        term2 = partials[beta, alpha, rho]
                        term3 = partials[rho, alpha, beta]
                        sum_term += g_contravariant[mu, rho] * (term1 + term2 - term3)
                    gamma[mu, alpha, beta] = 0.5 * sum_term
        return gamma

def schwarzschild_metric_function(mass, G=1.0, c=1.0):
    """
    Returns a metric function for a Schwarzschild spacetime profile.
    Coordinates: x = [t, r, theta, phi]
    Boundary conditions are checked inside the execution loops to preserve differentiability.
    """
    rs = 2 * G * mass / (c**2)
    def metric(x):
        t, r, theta, phi = x
        g = np.zeros((4, 4))
        g[0, 0] = -(1.0 - rs / r) * (c**2)
        g[1, 1] = 1.0 / (1.0 - rs / r)
        g[2, 2] = r**2
        g[3, 3] = (r**2) * np.sin(theta)**2
        return g
    return metric

def kerr_metric_function(mass, spin_a, G=1.0, c=1.0):
    """
    Returns the full Kerr metric tensor in Boyer-Lindquist coordinates.
    g_mu_nu components including cross-terms for frame-dragging effects.
    """
    def metric(x):
        t, r, theta, phi = x
        g = np.zeros((4, 4))
        
        Sigma = r**2 + (spin_a**2) * np.cos(theta)**2
        Delta = r**2 - 2*G*mass*r/(c**2) + spin_a**2
        
        g[0, 0] = -(1.0 - 2*G*mass*r/(c**2 * Sigma)) * (c**2)
        g[1, 1] = Sigma / Delta
        g[2, 2] = Sigma
        g[3, 3] = (r**2 + spin_a**2 + 2*G*mass*r*spin_a**2*np.sin(theta)**2/(c**2 * Sigma)) * np.sin(theta)**2
        
        g_t_phi = -2*G*mass*r*spin_a*np.sin(theta)**2 / (c**2 * Sigma)
        g[0, 3] = g_t_phi
        g[3, 0] = g_t_phi
        return g
    return metric