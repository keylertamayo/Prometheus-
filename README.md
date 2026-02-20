# AETHER Research Project

This repository contains a simplified prototype for the "Aether" autonomous learning agent described in the project blueprint. The aim is to simulate a software entity capable of self-reflection, memory management, task execution, and self-improvement.

## Structure

- `entity_core.py` – Implements `AetherEntity` with identity, objective, reflection and action logging.
- `memory_manager.py` – `MemoryManager` stores and retrieves key-value data in JSON format.
- `task_agent.py` – `TaskAgent` handles a simple queue of tasks and records results to memory.
- `self_improver.py` – `SelfImprover` analyzes code for TODO/FIXME patterns, proposes and tests improvements.
- `main.py` – Orchestrates all components in a loop for demonstration.

## Getting Started ⚙️

1. **Prerequisites**
   - Python 3.8+ installed in the environment.
   - (Optional) Create a virtual environment: `python -m venv venv && source venv/bin/activate`.

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt  # if any dependencies are added
   ```

3. **Run the main loop**
   ```bash
   python main.py
   ```

   The loop will run for 100 iterations by default, printing reflections, task results, and improvement proposals.

4. **Inspect memory**
   The file `memory.json` will be populated with stored entries from tasks and improvement tests.


## Development Instructions 📋

- Add new tasks via `agent.add_task(description)` in `main.py` or other modules.
- Extend `SelfImprover` analysis logic with real parsing.
- Use `MemoryManager` to persist agent state across runs.

This code is intentionally simple; it forms the basis for further experimentation in a controlled sandbox environment.
