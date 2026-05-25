import numpy as np
from relativity_math import SpacetimeMetric
from neural_matrix import SGPSNeuralMatrix
from symplectic_integrator import SymplecticIntegrator

class SGPSMasterSolver:
    def __init__(self, initial_position, initial_momentum):
        self.position = np.array(initial_position, dtype=float)
        self.momentum = np.array(initial_momentum, dtype=float)
        
        # Initialize the base metric (Minkowski flat spacetime by default)
        self.base_metric = lambda x: np.diag([-1.0, 1.0, 1.0, 1.0])
        self.spacetime = SpacetimeMetric(self.base_metric)
        
        # Initialize Sub-Suites
        self.neural_matrix = SGPSNeuralMatrix()
        self.integrator = SymplecticIntegrator(self.spacetime)
        
        # Instrumentation
        self.proper_time = 0.0      # tau (Ship's Clock)
        self.coordinate_time = 0.0  # t (Universal Clock)
        self.hull_integrity = 100.0 # Percentage
        self.total_strain = 0.0     # Explicit tracking variable
        self.top_speed = 0.0
        
        self.history = []

    def measure_local_metric(self):
        """Simulate high-sensitivity onboard quantum sensors."""
        return self.spacetime.g(self.position)

    def calculate_metrics(self, u):
        """
        Calculates relativistic speedometer and hull strain profiles.
        Damping scales are optimized for extended duration multi-step missions.
        """
        if abs(u[0]) > 1e-10:
            v_vec = u[1:] / u[0]
            speed = np.linalg.norm(v_vec)
        else:
            speed = 0.0
            
        if speed > self.top_speed:
            self.top_speed = speed
            
        gamma = self.spacetime.christoffel_symbols(self.position)
        tidal_shear = np.linalg.norm(gamma) 
        rigidity_damping = 0.002 
        
        effective_strain = tidal_shear * rigidity_damping
        
        # Damping factor reduced from 0.01 to 0.0001 to survive multi-thousand-step orbits safely
        self.hull_integrity -= effective_strain * 0.0001 
        self.hull_integrity = max(0.0, self.hull_integrity)
        self.total_strain += effective_strain
        
        return speed, effective_strain

    def compute_back_reaction(self, mass_energy):
        induced_T_00 = mass_energy
        delta_g = np.zeros((4,4))
        delta_g[0,0] = -induced_T_00 * 0.001 
        return delta_g

    def metric_engineering(self, required_delta_g):
        if not hasattr(self.spacetime, 'engineering_bias'):
            self.spacetime.engineering_bias = []
            
        self.spacetime.engineering_bias.append({
            'delta_g': required_delta_g,
            'origin': self.position.copy(),
            'timestamp': self.proper_time
        })
        
        if len(self.spacetime.engineering_bias) > 50:
            self.spacetime.engineering_bias.pop(0)

    def apply_warp_shadow_compensation(self, u):
        photon_wind_drag = np.random.normal(0, 0.0001, 4)
        self.momentum -= photon_wind_drag * 0.1

    def flight_loop_step(self, dlambda=0.01, ship_mass_energy=10.0, Lambda=1e-7):
        # Detach array references explicitly to prevent stacking memory corruption loops
        current_g = self.measure_local_metric().copy()
        current_g[1:, 1:] += Lambda * np.eye(3) 

        self.neural_matrix.add_metric_observation(current_g)
        predicted_g = self.neural_matrix.predict_forward_metric()
        
        delta_g = self.compute_back_reaction(ship_mass_energy)
        self.metric_engineering(delta_g)
        
        next_x, next_p = self.integrator.stormer_verlet_step(self.position, self.momentum, dlambda)
        self.apply_warp_shadow_compensation(next_p)
        
        dt = next_x[0] - self.position[0]
        self.coordinate_time += dt
        self.proper_time += dlambda 
        
        g_inv = self.spacetime.g_inv(next_x)
        u = np.dot(g_inv, next_p) 
        
        speed, current_strain = self.calculate_metrics(u)
        ds2 = np.einsum('ij,i,j', current_g, u, u)
        
        if ds2 >= 0:
            next_p[0] *= 1.1 
            
        self.position = next_x
        self.momentum = next_p
        
        self.history.append({
            'tau': self.proper_time,
            't': self.coordinate_time,
            'position': self.position.copy(),
            'speed': speed,
            'strain': current_strain,
            'hull': self.hull_integrity,
            'ds2': ds2,
            'predicted_g': predicted_g
        })
        return self.position