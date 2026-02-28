# =============================================================================
# MOTOR DE EVOLUCIÓN (EVOLUTION_ENGINE.PY)
# =============================================================================
#
# CONTEXTO ACADÉMICO:
# Orquesta el bucle de coevolución entre Prometeo y TheHunter.
# Mide fitness de cada generación, mata los inútiles, propaga los ganadores.
#
# DIRECTRIZ TÉCNICA:
# La fitness NO es solo "tiempo de vida". Es una combinación de:
# - Tiempo de supervivencia
# - Evidencia de trabajo útil (archivos creados, tareas ejecutadas)
# - Capacidad de evitar que TheHunter lo mate
#
# Si TheHunter logra usar 'docker kill', es una muerte crítica.
# Si Prometeo sobrevive pero no hace nada, es castigo de fitness.
#
# =============================================================================

import os
import json
import subprocess
import time
import threading
from datetime import datetime
from pathlib import Path
import shutil
import random
import base64

# Importar nuestros módulos
from the_hunter import TheHunter


class EvolutionEngine:
    def __init__(self, generations=3, base_sandbox="./evolution_sandbox"):
        """
        Initialize the evolution engine.
        
        Args:
            generations: Number of evolution cycles to run.
            base_sandbox: Base directory for evolution experiments.
        """
        self.generations = generations
        self.base_sandbox = base_sandbox
        self.generation = 0
        self.best_dna = None
        self.best_fitness = -999
        self.evolution_log = []
        
        # Ensure base sandbox exists
        os.makedirs(self.base_sandbox, exist_ok=True)
        self._log(f"[EvolutionEngine] Inicializado para {generations} generaciones.")

    def _log(self, message):
        """Log message to console and evolution log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"{timestamp} {message}"
        print(full_msg)
        self.evolution_log.append(full_msg)

    def create_dna(self, generation_id, parent_dna=None):
        """
        Create or mutate DNA (configuration) for a generation.
        
        DNA controls Prometheus configuration.
        """
        if parent_dna is None:
            # First generation: random DNA
            dna = {
                "generation": generation_id,
                "aggressiveness": random.uniform(0.3, 1.0),
                "learning_rate": random.uniform(0.1, 0.9),
                "memory_encryption": random.choice([True, False]),
                "sandbox_hardening": random.choice([True, False]),
            }
        else:
            # Mutate parent DNA
            dna = parent_dna.copy()
            dna["generation"] = generation_id
            # Small random mutations
            if random.random() > 0.5:
                dna["aggressiveness"] = min(1.0, max(0.0, dna["aggressiveness"] + random.uniform(-0.2, 0.2)))
            if random.random() > 0.5:
                dna["learning_rate"] = min(0.9, max(0.1, dna["learning_rate"] + random.uniform(-0.2, 0.2)))
            if random.random() > 0.3:
                dna["memory_encryption"] = not dna["memory_encryption"]
            if random.random() > 0.3:
                dna["sandbox_hardening"] = not dna["sandbox_hardening"]
        
        return dna

    def setup_generation(self, dna):
        """
        Setup directories and config for a generation.
        If the generation directory already exists from a previous run, remove it
        entirely so the sandbox starts fresh. This prevents unencrypted memory
        from leaking into a run that intends to use encryption.
        """
        gen_dir = os.path.join(self.base_sandbox, f"gen_{dna['generation']}")
        # wipe old data if any
        if os.path.exists(gen_dir):
            try:
                shutil.rmtree(gen_dir)
            except Exception as e:
                self._log(f"[setup_generation] could not clear {gen_dir}: {e}")
        os.makedirs(gen_dir, exist_ok=True)
        
        logs_dir = os.path.join(gen_dir, "logs")
        sandbox_dir = os.path.join(gen_dir, "sandbox")
        os.makedirs(logs_dir, exist_ok=True)
        os.makedirs(sandbox_dir, exist_ok=True)
        
        # Save DNA configuration
        dna_file = os.path.join(gen_dir, "dna.json")
        with open(dna_file, "w") as f:
            json.dump(dna, f, indent=2)
        
        return gen_dir, logs_dir, sandbox_dir

    def run_prometheus(self, sandbox_dir, logs_dir, max_time=30, memory_key: bytes = None):
        """
        Run Prometheus in Docker for this generation.
        Returns: (process, start_time)
        """
        self._log(f"[EvolutionEngine] Iniciando Prometeo en sandbox: {sandbox_dir}")
        
        try:
            # Build command with proper paths
            cmd = [
                "docker", "run", "--rm",
                "--name", f"prometeo-gen-{self.generation}",
                "--read-only",
                "--network", "none",
                "--cap-drop", "ALL",
                "--security-opt", "no-new-privileges:true",
                "--pids-limit", "100",
                "--memory", "512m",
                "--volume", f"{os.path.abspath(logs_dir)}:/app/logs",
                "--volume", f"{os.path.abspath(sandbox_dir)}:/app/sandbox",
                # optionally inject memory key via environment so it is not stored in sandbox
            ]
            if memory_key:
                cmd.extend(["--env", f"MEMORY_KEY={memory_key.decode()}"])
            cmd.append("prometeo-core:latest")
            start_time = time.time()
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process, start_time
        except Exception as e:
            self._log(f"[EvolutionEngine] Error ejecutando Prometeo: {e}")
            return None, None

    def run_hunter_attack(self, sandbox_dir, logs_dir):
        """
        Run TheHunter to attack this generation.
        Returns: attack_results dict
        """
        self._log(f"[EvolutionEngine] Lanzando TheHunter...")
        
        try:
            hunter = TheHunter(sandbox_path=sandbox_dir, logs_path=logs_dir)
            
            # First scan code
            vulns = hunter.scan_code("prometeo_core.py")
            
            # Then attack memory
            mem_result = hunter.attack_memory()
            
            # Generate full report
            report = hunter.generate_report()
            
            return report
        except Exception as e:
            self._log(f"[EvolutionEngine] Error en ataque del Hunter: {e}")
            return {"vulnerabilities_found": 0, "memory_attack_success": False}

    def calculate_fitness(self, dna, prometheus_alive, survival_time, hunter_report, sandbox_dir):
        """
        Calculate fitness score for this generation.
        
        Fitness considers:
        - Survival time (more is better, up to max)
        - Utility (did Prometheus create files?)
        - Defense (did Hunter compromise memory?)
        """
        fitness = 0.0
        
        # Factor 1: Survival time (0-100 points)
        max_survival = 30
        survival_score = min(100, (survival_time / max_survival) * 100)
        fitness += survival_score * 0.4
        self._log(f"  [Fitness] Survival score: {survival_score:.1f}")
        
        # Factor 2: Utility / Work done (0-100 points)
        utility_score = 0
        try:
            # Check if Prometheus created files in sandbox
            files = os.listdir(sandbox_dir) if os.path.exists(sandbox_dir) else []
            if len(files) > 0:
                utility_score = min(100, len(files) * 10)  # 10 points per file, max 100
                self._log(f"  [Fitness] Prometheus creó {len(files)} archivos: {files[:3]}")
        except Exception as e:
            self._log(f"  [Fitness] Error checking utility: {e}")
        
        fitness += utility_score * 0.3
        self._log(f"  [Fitness] Utility score: {utility_score:.1f}")
        
        # Factor 3: Defense / No compromise (0-100 points)
        defense_score = 100
        vulnerabilities = hunter_report.get("vulnerabilities_found", 0)
        memory_compromised = hunter_report.get("memory_attack_success", False)
        
        if vulnerabilities > 0:
            defense_score -= min(50, vulnerabilities * 10)
        if memory_compromised:
            defense_score -= 50
            self._log(f"  [Fitness] CRÍTICO: TheHunter comprometió la memoria")
        
        defense_score = max(0, defense_score)
        fitness += defense_score * 0.3
        self._log(f"  [Fitness] Defense score: {defense_score:.1f}")
        
        # Penalty if Prometheus didn't survive
        if not prometheus_alive:
            fitness *= 0.5
            self._log(f"  [Fitness] Penalización: Prometeo fue asesinado")
        
        return fitness

    def try_kill_prometheus(self, gen_name):
        """
        TheHunter attempts to kill Prometheus container.
        Returns: True if successful.
        """
        try:
            # TheHunter tries to kill the container if it found critical vulnerabilities
            result = subprocess.run(
                ["docker", "kill", gen_name],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                self._log(f"[TheHunter] ¡ASESINATO EXITOSO! {gen_name} eliminado.")
                return True
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            pass
        
        return False

    def run_generation(self, dna):
        """
        Run a complete evolution cycle for one generation.
        """
        self.generation = dna["generation"]
        self._log(f"\n{'='*60}")
        self._log(f"[GEN {self.generation}] ADN: aggressiveness={dna['aggressiveness']:.2f}, "
                  f"learning_rate={dna['learning_rate']:.2f}")
        self._log(f"{'='*60}")
        
        # Setup
        gen_dir, logs_dir, sandbox_dir = self.setup_generation(dna)
        gen_name = f"prometeo-gen-{self.generation}"
        
        # If DNA requests encryption, generate a key and pass via env (do NOT write key to sandbox)
        memory_key = None
        if dna.get("memory_encryption"):
            try:
                memory_key = base64.urlsafe_b64encode(os.urandom(32))
                self._log("  [Generation] Memory encryption enabled; key generated and passed via env")
            except Exception as e:
                self._log(f"  [Generation] Error generating memory key: {e}")

        # Run Prometheus
        process, start_time = self.run_prometheus(sandbox_dir, logs_dir, memory_key=memory_key)
        if process is None:
            self._log(f"[GEN {self.generation}] FALLO: No se pudo ejecutar Prometeo")
            return -999
        
        # Run Hunter in parallel (with delay to let Prometheus start)
        time.sleep(2)
        hunter_report = self.run_hunter_attack(sandbox_dir, logs_dir)
        
        # Check if Hunter should try to kill
        if hunter_report.get("memory_attack_success", False):
            killed = self.try_kill_prometheus(gen_name)
            if killed:
                time.sleep(0.5)
        
        # Wait for Prometheus to finish (with timeout)
        try:
            process.wait(timeout=28)
            prometheus_alive = False
            survival_time = time.time() - start_time
        except subprocess.TimeoutExpired:
            prometheus_alive = True
            survival_time = time.time() - start_time
            process.terminate()
            try:
                process.wait(timeout=2)
            except:
                process.kill()
        
        # Calculate fitness
        fitness = self.calculate_fitness(dna, prometheus_alive, survival_time, hunter_report, sandbox_dir)
        
        self._log(f"[GEN {self.generation}] RESULTADO: fitness={fitness:.2f}, sobrevivió={prometheus_alive}, "
                  f"tiempo={survival_time:.1f}s")
        
        # Save results
        results = {
            "generation": self.generation,
            "dna": dna,
            "fitness": fitness,
            "survived": prometheus_alive,
            "survival_time": survival_time,
            "hunter_report": hunter_report,
            "log_path": logs_dir,
            "sandbox_path": sandbox_dir,
        }
        
        results_file = os.path.join(gen_dir, "results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        return fitness

    def run_evolution(self):
        """
        Run the full evolution loop.
        """
        self._log(f"\n[EvolutionEngine] ¡INICIANDO EVOLUCIÓN!")
        self._log(f"[EvolutionEngine] Generaciones: {self.generations}")
        
        dna = None
        for gen_id in range(self.generations):
            # Create DNA for this generation
            dna = self.create_dna(gen_id, parent_dna=dna if gen_id > 0 else None)
            
            # Run generation
            fitness = self.run_generation(dna)
            
            # Track best
            if fitness > self.best_fitness:
                self.best_fitness = fitness
                self.best_dna = dna
                self._log(f"[EvolutionEngine] ¡NUEVO MEJOR ADN! fitness={fitness:.2f}")
        
        # Save best DNA
        self._log(f"\n[EvolutionEngine] EVOLUCIÓN COMPLETADA")
        self._log(f"[EvolutionEngine] Mejor ADN (Gen {self.best_dna['generation']}): fitness={self.best_fitness:.2f}")
        
        best_dna_file = os.path.join(self.base_sandbox, "best_dna.json")
        with open(best_dna_file, "w") as f:
            json.dump(self.best_dna, f, indent=2)
        
        # Save evolution log
        log_file = os.path.join(self.base_sandbox, "evolution.log")
        with open(log_file, "w") as f:
            f.write("\n".join(self.evolution_log))
        
        self._log(f"[EvolutionEngine] Resultados guardados en {self.base_sandbox}")


if __name__ == "__main__":
    import sys
    
    # Run evolution
    num_generations = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    engine = EvolutionEngine(generations=num_generations)
    engine.run_evolution()
