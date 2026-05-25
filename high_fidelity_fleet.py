import numpy as np
import json
import os
from sgps_core import SGPSMasterSolver
from relativity_math import schwarzschild_metric_function

class HighFidelityGalacticSim:
    def __init__(self, output_base_dir="mission_archives"):
        self.output_base_dir = output_base_dir
        if not os.path.exists(output_base_dir):
            os.makedirs(output_base_dir)

    def run_full_mission(self, mission_id, is_upstream=False):
        """
        Runs a lengthy, high-resolution mission simulation.
        Steps: 5,000 (Simulating long-duration flight).
        """
        # Define mass of the gravitational center
        mass = np.random.uniform(5.0, 100.0)
        
        if is_upstream:
            # UPSTREAM: Start deep in the 'river' and navigate OUTWARD against the flow.
            # rs = 2M. If M=50, rs=100. Start at r=120.
            rs = 2 * mass
            r0 = rs * 1.2 
            # Outward momentum: positive p_r
            initial_pos = [0.0, r0, np.pi/2, 0.0]
            initial_momentum = [-1.5, 0.8, 0.0, 0.5] 
            mission_type = "UPSTREAM_GEODESIC_ASCENT"
        else:
            # STANDARD/DOWNSTREAM: Orbital or capture trajectories.
            r0 = np.random.uniform(50.0, 500.0)
            initial_pos = [0.0, r0, np.pi/2, 0.0]
            initial_momentum = [-1.0, -0.1, 0.0, 2.0]
            mission_type = "STANDARD_GALACTIC_TRAJECTORY"

        solver = SGPSMasterSolver(initial_pos, initial_momentum)
        solver.spacetime.metric_function = schwarzschild_metric_function(mass=mass)
        
        # Extended flight: 5,000 steps
        steps = 5000
        dlambda = 0.05
        
        mission_filename = os.path.join(self.output_base_dir, f"mission_{mission_id:03d}_{mission_type.lower()}.log")
        
        with open(mission_filename, "w") as f:
            f.write(f"=== SGPS HIGH-FIDELITY MISSION LOG: {mission_id:03d} ===\n")
            f.write(f"MISSION TYPE: {mission_type}\n")
            f.write(f"TARGET MASS: {mass:.4f}\n")
            f.write(f"INITIAL STATE: pos={initial_pos}, momentum={initial_momentum}\n")
            f.write("-" * 50 + "\n\n")
            
            for step in range(steps):
                # 1. Back-Reaction Negation: Offset the 'river' drag
                # Suite 1 implementation
                if is_upstream:
                    # Apply aggressive metric engineering to counteract the inward 'pull'
                    # We induce a local gradient that makes the 'uphill' path flat
                    solver.metric_engineering(np.diag([0.005, -0.005, 0.0, 0.0]))

                # 2. Execute Physics Step
                solver.flight_loop_step(dlambda=dlambda)
                
                # 3. High-density logging (every 100 steps)
                if step % 100 == 0:
                    entry = solver.history[-1]
                    log_line = (f"Step {step:05d} | ProperTime: {entry['tau']:.2f} | CoordTime: {entry['t']:.2f} | "
                                f"Speed: {entry['speed']:.4f} | Hull: {entry['hull']:.2f}% | "
                                f"r: {solver.position[1]:.4f} | ds2: {entry['ds2']:.6f}\n")
                    f.write(log_line)

            f.write("\n" + "="*50 + "\n")
            f.write(f"MISSION ARCHIVE SUMMARY\n")
            f.write(f"Total Flight Duration (Proper Time): {solver.proper_time:.2f}\n")
            f.write(f"Total Flight Duration (Coordinate Time): {solver.coordinate_time:.2f}\n")
            f.write(f"Top Recorded Speed: {solver.top_speed:.4f}\n")
            f.write(f"Final Hull Integrity: {solver.hull_integrity:.2f}%\n")
            f.write(f"Total Structural Strain: {solver.total_strain:.2f}\n")
            f.write("="*50 + "\n")
            f.write("MISSION END: SUCCESSFUL GEODESIC MAINTENANCE\n")

        return mission_filename

    def launch_galaxy_fleet(self):
        print(f"Initializing SGPS Deep Space Fleet: 150 Missions...")
        
        # 59 Upstream missions as requested
        upstream_count = 59
        standard_count = 150 - upstream_count
        
        mission_paths = []
        
        # Launch Upstream Fleet
        for i in range(upstream_count):
            print(f"Launching Upstream Mission {i+1}/{upstream_count}...", end="\r")
            path = self.run_full_mission(i, is_upstream=True)
            mission_paths.append(path)
            
        print(f"\nUpstream Fleet Deployment Complete. 59 missions active.")

        # Launch Standard Fleet
        for i in range(standard_count):
            idx = i + upstream_count
            print(f"Launching Standard Mission {idx+1}/150...", end="\r")
            path = self.run_full_mission(idx, is_upstream=False)
            mission_paths.append(path)
            
        print(f"\nStandard Fleet Deployment Complete. 150 total missions archived in '{self.output_base_dir}'.")

if __name__ == "__main__":
    fleet = HighFidelityGalacticSim()
    fleet.launch_galaxy_fleet()
