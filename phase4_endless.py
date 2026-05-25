import numpy as np
import os
import time
from sgps_core import SGPSMasterSolver
from relativity_math import kerr_metric_function

def generate_realistic_target():
    """
    Generates target metrics for boundless simulation sweeps.
    Normalizes compact parameters using scale invariance to protect 
    64-bit numerical differentiators.
    """
    target_types = ["Supermassive Black Hole", "Stellar Black Hole", "Neutron Star", "Galactic Core"]
    target_type = np.random.choice(target_types)
    
    if target_type == "Supermassive Black Hole":
        mass = np.random.uniform(1.0, 10.0)  # Standardized local unit metric
        spin = np.random.uniform(0.5, 0.95) * mass
        r0_multiplier = np.random.uniform(1000, 3000)
    elif target_type == "Galactic Core":
        mass = np.random.uniform(10.0, 50.0) 
        spin = np.random.uniform(0.1, 0.5) * mass
        r0_multiplier = np.random.uniform(500, 1500)
    else: 
        # Low-mass bodies normalized to local units to protect float precision near horizon
        mass = np.random.uniform(1.0, 3.0)  
        spin = np.random.uniform(0.0, 0.8) * mass
        r0_multiplier = np.random.uniform(800, 2500)

    # Compute coordinate event horizon boundaries
    rs = 2.0 * mass
    r0 = rs * r0_multiplier
    return target_type, mass, spin, r0, rs

def run_endless_simulation():
    print("============================================================")
    print("SGPS PHASE 4: STABILIZED ENDLESS GALACTIC FLIGHT SIMULATOR")
    print("============================================================")
    print("Process running continuously. Press Ctrl+C to stop manually.\n")
    
    output_dir = "phase4_endless_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    mission_count = 1
    
    try:
        while True:
            target_type, mass, spin, r0, rs = generate_realistic_target()
            
            print(f"Mission {mission_count:04d} | Target: {target_type} | Orbit Radius: {r0:.2f}")
            
            # Setup stable initial orbital states [t, r, theta, phi]
            initial_pos = [0.0, r0, np.pi/2, 0.0]
            initial_momentum = [-1.0, 0.0, 0.0, r0 * 0.005]
            
            solver = SGPSMasterSolver(initial_pos, initial_momentum)
            solver.spacetime.metric_function = kerr_metric_function(mass=mass, spin_a=spin)
            
            steps = int(np.random.uniform(1500, 4000))
            dlambda = 1.0
            
            log_path = os.path.join(output_dir, f"route_{mission_count:04d}.log")
            
            with open(log_path, "w") as f:
                f.write(f"=== SGPS BOUNDLESS MISSION LOG {mission_count:04d} ===\n")
                f.write(f"TARGET MODEL: {target_type} | SYSTEM MASS: {mass:.4f} | SPIN INDICES: {spin:.4f}\n")
                f.write(f"START RADIUS: {r0:.2f} | CAPTURE THRESHOLD: {rs:.4f}\n")
                f.write("-" * 60 + "\n\n")
                
                mission_failed = False
                
                for step in range(steps):
                    # Intercept horizon crossing bounds cleanly to preserve program stability
                    if solver.position[1] <= rs + 1e-2:
                        f.write(f"\n[EVENT] CRITICAL THRESHOLD: Geodesic breached horizon boundary at r = {solver.position[1]:.4f}\n")
                        solver.hull_integrity = 0.0
                        mission_failed = True
                        break
                        
                    solver.flight_loop_step(dlambda=dlambda)
                    
                    if step % 200 == 0:
                        entry = solver.history[-1]
                        f.write(f"Step {step:05d} | Tau: {solver.proper_time:.1f} | Velocity: {entry['speed']:.4f} | Structural Shielding: {solver.hull_integrity:.2f}%\n")
                    
                    if solver.hull_integrity <= 0:
                        f.write("\n[CRASH] CRITICAL HULL INTEGRITY LOST\n")
                        mission_failed = True
                        break

                if not mission_failed and solver.hull_integrity > 0:
                    f.write("\nMISSION END: SUCCESSFUL FLIGHT PATH ARCHIVED\n")
                    print(f" -> Mission {mission_count:04d} Status: COMPLETED CLEANLY (Hull: {solver.hull_integrity:.1f}%)")
                else:
                    print(f" -> Mission {mission_count:04d} Status: VEHICLE LOG TERMINATED")
                    
            mission_count += 1
            time.sleep(0.4) # Control loop pacing
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Boundless flight processing sequence terminated by system operator.")

if __name__ == "__main__":
    run_endless_simulation()