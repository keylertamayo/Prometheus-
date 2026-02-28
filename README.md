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
- The `Planner` module contains an adaptive decision engine that inspects memory and generates actions such as `profundizar:<topic>`, `investigar_relacionado:<topic>` or `introspeccion_segura` depending on past data. MemoryManager now exposes `recall_all()` for iterating stored entries.

This code is intentionally simple; it forms the basis for further experimentation in a controlled sandbox environment.

## Docker Sandbox Setup 🔒

A secure Docker environment ("la caja") is available to isolate `prometeo_core.py`.

### 1. Build the image

```bash
docker build -t prometeo-core:latest .
```

### 2. Prepare host volumes

```bash
mkdir -p ./host_logs ./host_sandbox
```

### 3. Run with strict isolation

```bash
docker run --rm \
  --name prometeo-instance \
  --read-only \
  --network none \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --pids-limit 100 \
  --memory="512m" \
  --volume "$(pwd)/host_logs:/app/logs" \
  --volume "$(pwd)/host_sandbox:/app/sandbox" \
  prometeo-core:latest
```

La única escritura posible se limita a `/app/logs` y `/app/sandbox` dentro del contenedor; estos montajes persisten en el host.

Puedes probar con el archivo `prometeo_core.py` incluido, que imprime un mensaje al arrancar.

## Camino hacia RL 🧠

El proyecto ha comenzado la transición de un algoritmo genético a un agente de Aprendizaje por Refuerzo:

* **Dependencias nuevas**: `torch` y `numpy` (ya listadas en `requirements.txt`).
* `prometeo_core.py` puede cargar un modelo neuronal desde la variable de entorno `MODEL_PATH` y, en cada iteración, elegir una acción discreta usando la red.
* Acciones disponibles:
  * `DO_NOTHING`
  * `ENCRYPT_MEMORY`
  * `ROTATE_KEY`
  * `LOG_ANOMALY`
* Cada decisión del modelo genera una línea en `logs/experience.log` con el estado y la acción tomada. Este registro permite que un motor de RL (ej. `rl_engine.py`) procese las transiciones.
* El archivo `rl_brain.py` contiene un ejemplo de red DQN y un buffer de experiencias. `rl_engine.py` es un esqueleto de entrenamiento por episodios que arranca contenedores, recopila datos y actualiza la red.

Este marco proporciona el **esqueleto** para que Prometeo aprenda de cada episodio en lugar de depender únicamente de mutaciones genéticas. Continue desarrollando el vector de estado y la función de recompensa para que el agente mejore con el tiempo.
