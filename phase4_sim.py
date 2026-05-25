import numpy as np
import os
import time
from sgps_core import SGPSMasterSolver
from relativity_math import kerr_metric_function

def generate_realistic_target():
    """
    Generates random but stable metrics for simulation vectors.
    Mass constraints use localized scale invariance constants to protect double-precision math.
    """
    target_types = ["Supermassive Black Hole", "Stellar Black Hole", "Neutron Star", "Galactic Core"]
    target_type = np.random.choice(target_types)
    
    if target_type == "Supermassive Black Hole":
        mass = np.random.uniform(1.0, 10.0)  # Millions of solar masses
        spin = np.random.uniform(0.5, 0.95) * mass
        r0_multiplier = np.random.uniform(1000, 5000)
    elif target_type == "Galactic Core":
        mass = np.random.uniform(10.0, 100.0) 
        spin = np.random.uniform(0.1, 0.5) * mass
        r0_multiplier = np.random.uniform(500, 2000)
    else: 
        # Normalized localized coordinates to protect floating points near r=0 horizons
        mass = np.random.uniform(1.0, 5.0)  
        spin = np.random.uniform(0.0, 0.9) * mass
        r0_multiplier = np.random.uniform(1000, 5000)

    # Calculate physical horizon boundaries
    rs = 2.0 * mass
    r0 = rs * r0_multiplier
    return target_type, mass, spin, r0, rs

def run_endless_simulation():
    print("SGPS PHASE 4: BOUNDARY-VALIDATED GALACTIC SIMULATION")
    print("Press Ctrl+C to terminate the process manually.\n")
    
    output_dir = "phase4_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    mission_count = 1
    
    while True:
        target_type, mass, spin, r0, rs = generate_realistic_target()
        
        print(f"Mission {mission_count:04d} | Target: {target_type} | Mass: {mass:.4f} -> Initializing Route...")
        
        # Initializing equatorial frame coordinates [t, r, theta, phi]
        initial_pos = [0.0, r0, np.pi/2, 0.0]
        initial_momentum = [-1.0, 0.0, 0.0, r0 * 0.01]
        
        solver = SGPSMasterSolver(initial_pos, initial_momentum)
        solver.spacetime.metric_function = kerr_metric_function(mass=mass, spin_a=spin)
        
        steps = int(np.random.uniform(1000, 5000))
        dlambda = 1.0
        
        log_path = os.path.join(output_dir, f\"route_{mission_count:04d}.log\")
        
        with open(log_path, \"w\") as f:
            f.write(f\"=== SGPS PHASE 4 MISSION {mission_count:04d} ===\\n\")
            f.write(f\"TARGET: {target_type} | MASS: {mass:.4f} | SPIN: {spin:.4f}\\n\")
            f.write(f\"INITIAL RADIUS: {r0:.2f} | HORIZON RADIUS: {rs:.4f}\\n\")
            f.write(\"-\" * 60 + \"\\n\\n\")
            
            for step in range(steps):
                # Intercept horizon crossing boundary explicitly before math computation fails
                if solver.position[1] <= rs + 1e-3:
                    f.write(f\"\\n!!! CRITICAL COORDINATE APEX DETECTED !!!\\n\")
                    f.write(f\"Vessel reached event horizon threshold boundary at r = {solver.position[1]:.4f}\\n\")
                    solver.hull_integrity = 0.0
                    break
                    
                solver.flight_loop_step(dlambda=dlambda)
                
                if step % 200 == 0:
                    entry = solver.history[-1]
                    f.write(f\"Step {step:05d} | Tau: {solver.proper_time:.2f} | Speed: {entry['speed']:.4f} | Hull: {solver.hull_integrity:.2f}%\\n\")
                
                if solver.hull_integrity <= 0:
                    f.write(\"\\n!!! CRITICAL HULL FAILURE !!!\\n\")\n                    break

            if solver.hull_integrity > 0:
                f.write(\"\\nMISSION END: SUCCESSFUL ARRIVAL/MAINTENANCE\\n\")
                print(\"Status: SUCCESS\")
            else:
                print(\"Status: DESTROYED / HORIZON BREACH\")
                
        mission_count += 1
        time.sleep(0.5)

if __name__ == \"__main__\":
    try:
        run_endless_simulation()
    except KeyboardInterrupt:
        print(\"\\nPhase 4 Simulation manually terminated.\")