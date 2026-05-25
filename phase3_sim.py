import numpy as np
import os
from sgps_core import SGPSMasterSolver
from relativity_math import kerr_metric_function

def run_sgr_a_simulation():
    print("SGPS Real-World Simulation: Galactic Center (Sagittarius A*)")
    
    # Sgr A* parameters (in SI units, we scale for simulation)
    # Mass = 4.3 million solar masses
    # For simulation purposes, we use G=1, c=1 units. 
    # Let 1 Mass Unit = 1 Million Solar Masses
    m_sgr_a = 4.3 
    # Spin parameter (estimated 0.5 to 0.9)
    spin_a = 0.8 * m_sgr_a
    
    # Start at a distance comparable to the S-stars (e.g., S2)
    # S2 periapsis is ~120 AU. 
    # Schwarzschild radius for Sgr A* is ~0.08 AU.
    # So r0 ~ 1500 * Rs
    r0 = 1500.0 * (2 * m_sgr_a) 
    
    initial_pos = [0.0, r0, np.pi/2, 0.0]
    # Elliptical orbit momentum
    initial_momentum = [-1.0, 0.0, 0.0, 150.0]
    
    solver = SGPSMasterSolver(initial_pos, initial_momentum)
    solver.spacetime.metric_function = kerr_metric_function(mass=m_sgr_a, spin_a=spin_a)
    
    steps = 10000
    dlambda = 1.0
    
    output_dir = "real_world_archive"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    log_path = os.path.join(output_dir, "sgr_a_orbital.log")
    
    with open(log_path, "w") as f:
        f.write("=== SGPS REAL-WORLD MISSION: SAGITTARIUS A* ORBIT ===\n")
        f.write(f"CENTRAL MASS: {m_sgr_a}M Sol | SPIN: {spin_a}\n")
        f.write("-" * 60 + "\n\n")
        
        for step in range(steps):
            solver.flight_loop_step(dlambda=dlambda)
            
            if step % 500 == 0:
                entry = solver.history[-1]
                f.write(f"Step {step:05d} | Tau: {solver.proper_time:.2f} | Speed: {entry['speed']:.6f} | Hull: {solver.hull_integrity:.2f}%\n")
                print(f"Mission SgrA* | Proper Time: {solver.proper_time:.2f} | Hull: {solver.hull_integrity:.2f}%", end="\r")

        f.write("\n" + "="*60 + "\n")
        f.write(f"REAL-WORLD DATA SUMMARY\n")
        f.write(f"Total Duration (Proper): {solver.proper_time:.2f}\n")
        f.write(f"Top Relativistic Speed: {solver.top_speed:.6f}\n")
        f.write(f"Final Hull Integrity: {solver.hull_integrity:.2f}%\n")
        f.write("="*60 + "\n")

    print(f"\nReal-world Sgr A* simulation log saved to {log_path}")

if __name__ == "__main__":
    run_sgr_a_simulation()
