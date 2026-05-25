#!/bin/bash

# Define scripts and labels
SCRIPTS=("phase1_sim.py" "phase2_sim.py" "phase3_sim.py" "phase4_sim.py" "batch_test.py")
LABELS=("Phase 1 Simulation" "Phase 2 Simulation" "Phase 3 Simulation" "Phase 4 Simulation" "Batch Test")

# Display menu
echo "Select a simulation to run:"
for i in "${!LABELS[@]}"; do
    echo "$((i+1)). ${LABELS[$i]}"
done

# Wait for user input
read -p "Enter selection (1-${#LABELS[@]}): " CHOICE

# Validate input and set script
if [[ "$CHOICE" -ge 1 && "$CHOICE" -le "${#LABELS[@]}" ]]; then
    SELECTED_SCRIPT="${SCRIPTS[$((CHOICE-1))]}"
    SELECTED_LABEL="${LABELS[$((CHOICE-1))]}"
else
    echo "Invalid selection."
    exit 1
fi

SESSION_NAME="sgps_sims"
# Generate a simple window name
WINDOW_NAME=$(echo "$SELECTED_LABEL" | tr -d ' ' | tr '[:upper:]' '[:lower:]' | cut -c1-10)

# Check if session exists
tmux has-session -t "$SESSION_NAME" 2>/dev/null

if [ $? != 0 ]; then
    # Create new session with the selected script
    tmux new-session -d -s "$SESSION_NAME" -n "$WINDOW_NAME" "./.venv/bin/python $SELECTED_SCRIPT; exec bash"
else
    # Create new window in existing session
    tmux new-window -t "$SESSION_NAME" -n "$WINDOW_NAME" "./.venv/bin/python $SELECTED_SCRIPT; exec bash"
fi

# Attach to the session
tmux attach -t "$SESSION_NAME"
