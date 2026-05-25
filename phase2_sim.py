import numpy as np
import os
from sgps_core import SGPSMasterSolver
from relativity_math import schwarzschild_metric_function

def run_lost_in_space():
    print("WARNING: Launching 'Lost in Space' Endurance Mission...")
    print("Scenario: Craft stranded at the edge of the galaxy, high distance, high metric turbulence.")
    
    # Start at a massive distance: r=2000
    initial_pos = [0.0, 2000.0, np.pi/2, 0.0]
    # Headed home (negative p_r) with high momentum
    initial_momentum = [-2.0, -1.5, 0.0, 10.0]
    
    # Destination home: A massive galactic core (Mass=500)
    home_mass = 500.0
    
    solver = SGPSMasterSolver(initial_pos, initial_momentum)
    solver.spacetime.metric_function = schwarzschild_metric_function(mass=home_mass)
    
    # Ultra-long duration: 25,000 steps
    steps = 25000
    dlambda = 0.1
    
    output_dir = "lost_in_space_archive"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    log_path = os.path.join(output_dir, "endurance_return.log")
    
    with open(log_path, "w") as f:
        f.write("=== SGPS 'LOST IN SPACE' ENDURANCE MISSION ===\n")
        f.write(f"STARTING RADIUS: 2000.0 | TARGET MASS (HOME): {home_mass}\n")
        f.write("-" * 60 + "\n\n")
        
        for step in range(steps):
            # Dynamic hull degradation is now handled in sgps_core.py
            
            # Execute SGPS Step
            solver.flight_loop_step(dlambda=dlambda)
            
            if step % 500 == 0:
                entry = solver.history[-1]
                status = "CRITICAL" if solver.hull_integrity < 20 else "STABLE"
                f.write(f"Log {step:05d} | Tau: {solver.proper_time:.2f} | Hull: {solver.hull_integrity:.2f}% | "
                        f"r: {solver.position[1]:.2f} | Speed: {entry['speed']:.4f} | Status: {status}\n")
                print(f"Distance to Home: {solver.position[1]:.2f} | Hull: {solver.hull_integrity:.2f}%", end="\r")
                
            if solver.hull_integrity <= 0:
                f.write("\n!!! HULL FAILURE: VESSEL DECOMPRESSED IN INTERSTELLAR SPACE !!!\n")
                print("\nMISSION FAILURE: HULL COMPROMISED.")
                break
                
            if solver.position[1] < 1000 and step > 5000:
                # Approaching high curvature zone
                if step % 500 == 0:
                    f.write(">> Entering Galactic Core proximity. Tidal forces increasing.\n")

        f.write("\n" + "="*60 + "\n")
        f.write(f"ENDURANCE SUMMARY\n")
        f.write(f"Total Flight Time (Proper): {solver.proper_time:.2f}\n")
        f.write(f"Top Speed: {solver.top_speed:.4f}\n")
        f.write(f"Final Hull Status: {solver.hull_integrity:.2f}%\n")
        f.write("="*60 + "\n")

    print(f"\nEndurance log saved to {log_path}")

if __name__ == "__main__":
    run_lost_in_space()
