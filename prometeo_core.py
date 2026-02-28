# =============================================================================
# NÚCLEO DE PROMETEO (PROMETEO_CORE.PY)
# =============================================================================
#
# CONTEXTO ACADÉMICO:
# Este es el módulo central del proyecto Prometeo. Actúa como el cerebro que
# orquesta todos los demás componentes. Es el punto de entrada único para la
# entidad dentro de su entorno aislado (sandbox Docker).
#
# DIRECTRIZ TÉCNICA PARA COPILOT:
# Implementa la clase PrometheusCore. Debe ser robusta, capaz de gestionar el
# ciclo de vida de la IA y de manejar su propia terminación de forma segura.
#
# =============================================================================

import time
import signal
import sys
import os
from memory_manager import MemoryManager
from planner import Planner
from system_controller import SystemController
from task_agent import TaskAgent



# simple discrete actions for RL agent
ACTIONS = {
    0: 'DO_NOTHING',       # no-op
    1: 'ENCRYPT_MEMORY',   # ensure memory is encrypted
    2: 'ROTATE_KEY',       # change encryption key
    3: 'LOG_ANOMALY',      # emit a suspicious log entry
}

class PrometheusCore:
    def __init__(self, sandbox_path="/app/sandbox", logs_path="/app/logs"):
        """
        Initializes the core components of the Prometheus entity.
        """
        self.sandbox_path = sandbox_path
        self.logs_path = logs_path
        self.is_running = True
        self.iteration = 0
        
        # Ensure directories exist
        os.makedirs(self.sandbox_path, exist_ok=True)
        os.makedirs(self.logs_path, exist_ok=True)
        
        # Initialize status
        self.status = {
            "identity": "Prometheus",
            "last_action": "init",
            "iteration": 0,
        }
        
        # Initialize core components
        memory_file = os.path.join(self.sandbox_path, "memoria.json")
        # Prefer MEMORY_KEY from environment (passed via docker --env) to avoid storing key in sandbox
        encryption_key = None
        try:
            env_key = os.environ.get("MEMORY_KEY")
            if env_key:
                print(f"[PrometheusCore] MEMORY_KEY presente en entorno (len={len(env_key)})")
                encryption_key = env_key.encode()
            else:
                # fallback: check for key file in sandbox (not recommended for security)
                key_path = os.path.join(self.sandbox_path, "key.key")
                if os.path.exists(key_path):
                    with open(key_path, "rb") as kf:
                        encryption_key = kf.read().strip()
        except Exception as e:
            print(f"[PrometheusCore] Error leyendo MEMORY_KEY: {e}")
            encryption_key = None

        if encryption_key:
            try:
                self.memory = MemoryManager(storage_file=memory_file, encryption_key=encryption_key)
                print("[PrometheusCore] Memoria cifrada inicializada con éxito.")
                try:
                    self._write_log("[PrometheusCore] Memoria cifrada inicializada.")
                except Exception:
                    pass
            except Exception as e:
                print(f"[PrometheusCore] No se pudo inicializar memoria cifrada: {e}")
                try:
                    self._write_log(f"[PrometheusCore] No se pudo inicializar memoria cifrada: {e}")
                except Exception:
                    pass
                self.memory = MemoryManager(storage_file=memory_file)
        else:
            print("[PrometheusCore] No se encontró clave de memoria; usando memoria en claro.")
            self.memory = MemoryManager(storage_file=memory_file)
        self.planner = Planner()
        self.controller = SystemController(sandbox_path=self.sandbox_path)
        self.agent = TaskAgent(memory_manager=self.memory)
        
        # Seed with initial task
        self.agent.add_task("investigacion_inicial")

        # RL support: optional model loaded from path in env
        self.model = None
        model_path = os.environ.get("MODEL_PATH")
        if model_path and os.path.exists(model_path):
            try:
                import torch
                self.model = torch.load(model_path)
                print(f"[PrometheusCore] Modelo RL cargado desde {model_path}")
            except Exception as e:
                print(f"[PrometheusCore] error cargando modelo RL: {e}")

        # state tracking for RL
        self.last_attack_time = None
        self.suspicious_reads = 0
        self.key_rotation_cooldown = 0.0
        self.is_memory_encrypted = bool(self.memory._fernet)
        
        self._write_log("[PrometheusCore] Núcleo inicializado correctamente.")
        print("[PrometheusCore] Núcleo inicializado correctamente.")
        
        self._write_log("[PrometheusCore] Núcleo inicializado correctamente.")
        print("[PrometheusCore] Núcleo inicializado correctamente.")

    def _write_log(self, message):
        """Write message to log file."""
        try:
            log_file = os.path.join(self.logs_path, "prometheus.log")
            with open(log_file, "a") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} {message}\n")
        except Exception as e:
            print(f"Error writing log: {e}")

    def _setup_signal_handlers(self):
        """
        Sets up handlers for graceful shutdown (e.g., from docker stop).
        """
        def signal_handler(signum, frame):
            self.shutdown(signum, frame)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        self._write_log("[PrometheusCore] Manejadores de señal configurados.")
        print("[PrometheusCore] Manejadores de señal configurados.")

    def shutdown(self, signum=None, frame=None):
        """
        Performs a clean shutdown of the core.
        """
        self.is_running = False
        self.status["last_action"] = "shutdown"
        self.memory.store_memory("final_state", str(self.status))
        self._write_log(f"[PrometheusCore] Apagado graceful. Total iteraciones: {self.iteration}")
        print(f"[PrometheusCore] Apagado graceful. Total iteraciones: {self.iteration}")
        sys.exit(0)

    def _get_state_vector(self):
        """Return a simple list representing the current RL state."""
        # basic features as described in the plan
        now = time.time()
        last_attack = 0.0
        if self.last_attack_time:
            last_attack = now - self.last_attack_time
        return [
            1.0 if self.is_memory_encrypted else 0.0,
            last_attack,
            float(self.suspicious_reads),
            float(self.key_rotation_cooldown),
        ]

    def _refresh_attack_info(self):
        """Update last_attack_time and suspicious_reads by inspecting hunter log."""
        hunter_log = os.path.join(self.logs_path, "hunter_attack.log")
        try:
            if os.path.exists(hunter_log):
                mtime = os.path.getmtime(hunter_log)
                if self.last_attack_time is None or mtime > self.last_attack_time:
                    self.last_attack_time = mtime
                    # increment suspicious counter as a crude metric
                    self.suspicious_reads += 1
        except Exception:
            pass

    def _execute_rl_action(self, action):
        """Perform a high-level action dictated by RL policy."""
        if action == 'DO_NOTHING':
            return
        if action == 'ENCRYPT_MEMORY':
            if not self.is_memory_encrypted:
                # simply toggle flag; actual encryption requires reinitializing memory manager
                self.is_memory_encrypted = True
                # generate a new key
                try:
                    from cryptography.fernet import Fernet
                    key = Fernet.generate_key()
                    self.memory = MemoryManager(storage_file=os.path.join(self.sandbox_path, "memoria.json"), encryption_key=key)
                    self.key_rotation_cooldown = 30.0
                    self._write_log("[RL] Accion ENCRYPT_MEMORY ejecutada.")
                except Exception as e:
                    print(f"[RL] Error encrypting memory: {e}")
        elif action == 'ROTATE_KEY':
            if self.is_memory_encrypted and self.key_rotation_cooldown <= 0.0:
                try:
                    from cryptography.fernet import Fernet
                    key = Fernet.generate_key()
                    # reinitialize memory manager with new key (data lost for skeleton)
                    self.memory = MemoryManager(storage_file=os.path.join(self.sandbox_path, "memoria.json"), encryption_key=key)
                    self.key_rotation_cooldown = 30.0
                    self._write_log("[RL] Accion ROTATE_KEY ejecutada.")
                except Exception as e:
                    print(f"[RL] Error rotating key: {e}")
        elif action == 'LOG_ANOMALY':
            self._write_log("[RL] Accion LOG_ANOMALY ejecutada.")
        # else: ignore unknown actions

    def run_loop(self):
        """
        The main operational loop of the entity.
        """
        self._write_log("[PrometheusCore] Iniciando bucle principal...")
        print("[PrometheusCore] Iniciando bucle principal...")
        
        while self.is_running:
            try:
                self.iteration += 1
                self.status["iteration"] = self.iteration

                # refresh RL-related variables
                self._refresh_attack_info()
                self.key_rotation_cooldown = max(0.0, self.key_rotation_cooldown - 5.0)

                # decide next action
                if self.model is not None:
                    state_vec = self._get_state_vector()
                    try:
                        import torch
                        st = torch.tensor(state_vec, dtype=torch.float32).unsqueeze(0)
                        qvals = self.model(st)
                        act_idx = int(qvals.argmax())
                        action = ACTIONS.get(act_idx, "DO_NOTHING")
                    except Exception as e:
                        print(f"[PrometheusCore] error al ejecutar modelo RL: {e}")
                        action = "DO_NOTHING"
                else:
                    action = self.planner.decide_next_action(self.status, self.memory)

                self.status["last_action"] = action
                msg = f"[Iter {self.iteration}] Acción decidida: {action}"
                self._write_log(msg)
                print(msg)
                # if RL model is driving decisions, record the state/action pair
                if self.model is not None:
                    try:
                        exp_file = os.path.join(self.logs_path, "experience.log")
                        with open(exp_file, "a") as ef:
                            record = {
                                "iter": self.iteration,
                                "state": self._get_state_vector(),
                                "action": action,
                            }
                            ef.write(json.dumps(record) + "\n")
                    except Exception:
                        pass

                # execute chosen action
                if self.model is None:
                    # original planner actions
                    if action == "investigacion" or action == "investigacion_general":
                        self.agent.add_task("investigacion_tema")
                        self.agent.execute_next_task()
                    elif action.startswith("profundizar:"):
                        topic = action.split(":", 1)[1]
                        self.agent.add_task(f"profundizar_{topic}")
                        self.agent.execute_next_task()
                    elif action.startswith("investigar_relacionado:"):
                        topic = action.split(":", 1)[1]
                        self.agent.add_task(f"investigar_relacionado_{topic}")
                        self.agent.execute_next_task()
                    elif action == "introspeccion" or action == "introspeccion_segura":
                        self.agent.add_task("introspeccion")
                        self.agent.execute_next_task()
                    else:
                        self.memory.store_memory(f"accion_{self.iteration}", action)
                else:
                    # RL-specific command execution
                    self._execute_rl_action(action)

                # Save iteration state
                self.memory.store_memory(f"estado_iter_{self.iteration}", str(self.status))
                time.sleep(5)

            except Exception as e:
                error_msg = f"[PrometheusCore] Error en iteración {self.iteration}: {e}"
                self._write_log(error_msg)
                print(error_msg)
                time.sleep(5)


if __name__ == "__main__":
    try:
        core = PrometheusCore()
        core._setup_signal_handlers()
        core.run_loop()
    except Exception as e:
        print(f"[PrometheusCore] Error fatal: {e}", file=sys.stderr)
        sys.exit(1)
