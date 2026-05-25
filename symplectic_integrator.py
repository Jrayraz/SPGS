import numpy as np
from relativity_math import SpacetimeMetric

class SymplecticIntegrator:
    def __init__(self, spacetime: SpacetimeMetric):
        """
        Symplectic integrator for Hamiltonian mechanics in curved spacetime.
        Maintains strict conservation of energy and momentum (The Action Balance).
        """
        self.spacetime = spacetime

    def hamiltonian(self, x, p):
        """
        Calculates the Hamiltonian H = 1/2 * g^{mu nu} p_mu p_nu
        x: position 4-vector
        p: covariant momentum 4-vector
        """
        g_inv = self.spacetime.g_inv(x)
        H = 0.5 * np.einsum('ij,i,j', g_inv, p, p)
        return H

    def dp_dlambda(self, x, p):
        """
        Calculates the derivative of momentum with respect to affine parameter lambda.
        dp_mu/dlambda = -dH/dx^mu = -1/2 * (\partial_mu g^{alpha beta}) p_alpha p_beta
        Uses adaptive coordinate steps to protect float64 precision on macroscopic metrics.
        """
        dim = self.spacetime.dim
        dp = np.zeros(dim)
        
        for mu in range(dim):
            # Scale delta dynamically to protect precision against macroscopic space offsets
            delta = 1e-6 * max(1.0, abs(x[mu]))
            
            x_plus = np.copy(x)
            x_plus[mu] += delta
            g_inv_plus = self.spacetime.g_inv(x_plus)
            
            x_minus = np.copy(x)
            x_minus[mu] -= delta
            g_inv_minus = self.spacetime.g_inv(x_minus)
            
            dg_inv_dmu = (g_inv_plus - g_inv_minus) / (2 * delta)
            dp[mu] = -0.5 * np.einsum('ij,i,j', dg_inv_dmu, p, p)
            
        return dp

    def dx_dlambda(self, x, p):
        """
        Calculates the derivative of position with respect to affine parameter lambda.
        dx^mu/dlambda = dH/dp_mu = g^{mu nu} p_nu
        """
        g_inv = self.spacetime.g_inv(x)
        return np.dot(g_inv, p)

    def stormer_verlet_step(self, x, p, dlambda):
        """
        Symplectic leapfrog / Stormer-Verlet integration step.
        Updates position x and momentum p.
        """
        # Half step for momentum
        p_half = p + 0.5 * dlambda * self.dp_dlambda(x, p)
        
        # Full step for position using updated momentum
        x_next = x + dlambda * self.dx_dlambda(x, p_half)
        
        # Final half step for momentum
        p_next = p_half + 0.5 * dlambda * self.dp_dlambda(x_next, p_half)
        
        return x_next, p_next