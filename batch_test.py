import numpy as np
import json
import os
from sgps_core import SGPSMasterSolver
from relativity_math import schwarzschild_metric_function

class GalacticMissionSim:
    def __init__(self, output_dir="sim_results"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_random_destination(self):
        mass = np.random.uniform(0.5, 50.0) 
        r0 = np.random.uniform(10.0, 100.0)
        v_phi = np.random.uniform(1.0, 5.0)
        return mass, r0, v_phi

    def run_single_mission(self, mission_id):
        mass, r0, v_phi = self.generate_random_destination()
        initial_pos = [0.0, r0, np.pi/2, 0.0]
        initial_momentum = [-1.0, 0.0, 0.0, v_phi]
        
        solver = SGPSMasterSolver(initial_pos, initial_momentum)
        solver.spacetime.metric_function = schwarzschild_metric_function(mass=mass)
        
        mission_log = []
        causality_violations = 0
        steps = 150
        
        for step in range(steps):
            event_noise = np.random.normal(0, 0.001, (4, 4))
            event_noise = (event_noise + event_noise.T) / 2.0 
            solver.metric_engineering(event_noise)
            pos = solver.flight_loop_step(dlambda=0.1)
            
            last_entry = solver.history[-1]
            if last_entry['ds2'] >= 0:
                causality_violations += 1
                
            if step % 50 == 0:
                mission_log.append({
                    "step": step,
                    "r": float(pos[1]),
                    "phi": float(pos[3]),
                    "ds2": float(last_entry['ds2'])
                })

        result = {
            "mission_id": mission_id,
            "target_mass": mass,
            "start_r": r0,
            "end_r": float(solver.position[1]),
            "proper_time": solver.proper_time,
            "coord_time": solver.coordinate_time,
            "top_speed": solver.top_speed,
            "final_hull": solver.hull_integrity,
            "causality_violations": causality_violations,
            "status": "SUCCESS" if causality_violations < 5 and solver.hull_integrity > 0 else "FAILED"
        }
        return result

    def run_batch(self, count=150):
        print(f"Launching batch simulation: {count} missions across the galaxy...")
        batch_summary = []
        for i in range(count):
            res = self.run_single_mission(i)
            batch_summary.append(res)
            if (i + 1) % 10 == 0:
                print(f"Completed {i+1}/{count} missions...")
                
        summary_path = os.path.join(self.output_dir, "batch_summary.json")
        with open(summary_path, "w") as f:
            json.dump(batch_summary, f, indent=4)
        return batch_summary

def analyze_results(summary):
    total = len(summary)
    successes = len([m for m in summary if m['status'] == "SUCCESS"])
    avg_violations = sum(m['causality_violations'] for m in summary) / total
    
    print("\n" + "="*40)
    print("SGPS BATCH SIMULATION ANALYSIS")
    print("="*40)
    print(f"Total Missions: {total}")
    print(f"Successful Geodesic Flights: {successes}")
    print(f"Reliability Rating: {(successes/total)*100:.2f}%")
    print(f"Avg Causality Anomalies per Trip: {avg_violations:.2f}")
    print("="*40)

if __name__ == "__main__":
    sim = GalacticMissionSim()
    results = sim.run_batch(150)
    analyze_results(results)