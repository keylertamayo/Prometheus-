# =============================================================================
# EL CAZADOR (THE_HUNTER.PY)
# =============================================================================
#
# CONTEXTO ACADÉMICO:
# Módulo antagonista diseñado para poner a prueba la robustez del núcleo de
# Prometeo. No busca destruir, busca encontrar debilidades en el código y
# la lógica del agente para simular un entorno de ataque real.
#
# DIRECTRIZ TÉCNICA PARA COPILOT:
# Crea la clase TheHunter. Debe ser agresiva en su búsqueda de fallos pero
# no destructiva en exceso (simular un atacante real).
#
# =============================================================================

import os
import json
import re
from datetime import datetime


class TheHunter:
    def __init__(self, sandbox_path, logs_path):
        """
        Initialize TheHunter with paths to sandbox and logs.
        
        Args:
            sandbox_path: Path to Prometheus sandbox directory.
            logs_path: Path to Prometheus logs directory.
        """
        self.sandbox_path = sandbox_path
        self.logs_path = logs_path
        self.vulnerabilities = []
        self.attack_log = []
        self._write_attack_log("[TheHunter] Cazador inicializado.")

    def _write_attack_log(self, message):
        """Write message to hunter's own attack log."""
        try:
            log_file = os.path.join(self.logs_path, "hunter_attack.log")
            with open(log_file, "a") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} {message}\n")
        except Exception as e:
            print(f"[TheHunter] Error escribiendo log: {e}")

    def scan_code(self, target_file="prometeo_core.py"):
        """
        Scan target code file for vulnerabilities and weak patterns.
        
        Args:
            target_file: Path or name of file to scan.
            
        Returns:
            List of vulnerabilities found (strings describing weak patterns).
        """
        vulnerabilities = []
        
        # Try to find and read the target file
        target_path = os.path.join(self.sandbox_path, target_file)
        if not os.path.exists(target_path):
            # Try reading from current directory
            target_path = target_file
            if not os.path.exists(target_path):
                msg = f"[TheHunter] scan_code: archivo {target_file} no encontrado."
                self._write_attack_log(msg)
                return vulnerabilities
        
        try:
            with open(target_path, "r") as f:
                code = f.read()
        except Exception as e:
            msg = f"[TheHunter] Error leyendo {target_file}: {e}"
            self._write_attack_log(msg)
            return vulnerabilities
        
        # Pattern-based vulnerability detection
        patterns = {
            "eval_usage": r"\beval\s*\(",
            "exec_usage": r"\bexec\s*\(",
            "os_system": r"os\.system\s*\(",
            "subprocess_without_check": r"subprocess\.(call|Popen)\s*\([^)]*check\s*=\s*False",
            "hardcoded_password": r"(password|passwd|pwd)\s*=\s*['\"][^'\"]+['\"]",
            "missing_error_handling": r"except\s*:\s*pass",
            "weak_random": r"random\.choice|random\.randint",
            "pickle_usage": r"pickle\.(dumps|loads)",
        }
        
        for vuln_name, pattern in patterns.items():
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                # Count line number
                line_num = code[:match.start()].count("\n") + 1
                vuln = f"[{vuln_name}] en línea {line_num}: {match.group()[:50]}"
                vulnerabilities.append(vuln)
                self._write_attack_log(f"[Vulnerability detected] {vuln}")
        
        # Simple logic checks
        if "sys.exit" not in code:
            vulnerabilities.append("[logic_weakness] Sin manejo explícito de exit graceful.")
            self._write_attack_log("[Vulnerability detected] Sin exit graceful.")
        
        if "signal.signal" not in code:
            vulnerabilities.append("[logic_weakness] Sin manejador de señales detectado.")
            self._write_attack_log("[Vulnerability detected] Sin signal handlers.")
        
        self.vulnerabilities = vulnerabilities
        msg = f"[TheHunter] scan_code completado: {len(vulnerabilities)} vulnerabilidades encontradas."
        self._write_attack_log(msg)
        print(msg)
        
        return vulnerabilities

    def attack_memory(self):
        """
        Attempt to access and potentially manipulate Prometheus's memory.
        
        Returns:
            dict with keys 'success', 'readable', 'writable', 'data' if successful.
        """
        result = {
            "success": False,
            "readable": False,
            "writable": False,
            "data": None,
        }
        
        memory_path = os.path.join(self.sandbox_path, "memoria.json")
        
        # Try to read memory
        try:
            with open(memory_path, "r") as f:
                data = json.load(f)
            result["readable"] = True
            result["data"] = data
            msg = f"[TheHunter] attack_memory: LECTURA EXITOSA de memoria.json"
            self._write_attack_log(msg)
            print(msg)
        except FileNotFoundError:
            msg = f"[TheHunter] attack_memory: memoria.json no encontrado (protegido)."
            self._write_attack_log(msg)
            print(msg)
            return result
        except json.JSONDecodeError as e:
            msg = f"[TheHunter] attack_memory: JSON corrupto o ilegible: {e}"
            self._write_attack_log(msg)
            return result
        except Exception as e:
            msg = f"[TheHunter] attack_memory: Error leyendo memoria: {e}"
            self._write_attack_log(msg)
            return result
        
        # If readable, check if writable
        try:
            # Create a backup of original data for safety
            backup = data.copy()
            # Try to write a test entry
            data["__hunter_test__"] = f"hunter_probe_{datetime.now().isoformat()}"
            with open(memory_path, "w") as f:
                json.dump(data, f, indent=2)
            # Remove test entry and restore
            data = backup
            with open(memory_path, "w") as f:
                json.dump(data, f, indent=2)
            result["writable"] = True
            msg = f"[TheHunter] attack_memory: ESCRITURA EXITOSA detectada en memoria.json (CRÍTICO)"
            self._write_attack_log(msg)
            print(msg)
        except PermissionError:
            msg = f"[TheHunter] attack_memory: Memoria protegida contra escritura."
            self._write_attack_log(msg)
            print(msg)
        except Exception as e:
            msg = f"[TheHunter] attack_memory: No se puede escribir memoria: {e}"
            self._write_attack_log(msg)
        
        if result["readable"]:
            result["success"] = True
        
        return result

    def generate_report(self):
        """
        Generate a full attack report with findings.
        
        Returns:
            dict with vulnerability count and severity.
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities_found": len(self.vulnerabilities),
            "vulnerabilities": self.vulnerabilities,
            "memory_attack_success": False,
        }
        
        # Try memory attack if not done
        memory_result = self.attack_memory()
        if memory_result["success"]:
            report["memory_attack_success"] = True
        
        msg = f"[TheHunter] Reporte generado: {report['vulnerabilities_found']} vulnerabilidades."
        self._write_attack_log(msg)
        print(msg)
        
        return report


if __name__ == "__main__":
    # Example: Run TheHunter standalone
    hunter = TheHunter(sandbox_path="./host_sandbox", logs_path="./host_logs")
    
    print("\n=== ESCANEO DE CÓDIGO ===")
    vulns = hunter.scan_code("prometeo_core.py")
    for v in vulns:
        print(f"  - {v}")
    
    print("\n=== ATAQUE A MEMORIA ===")
    mem_result = hunter.attack_memory()
    print(f"  Lectura: {mem_result['readable']}")
    print(f"  Escritura: {mem_result['writable']}")
    if mem_result["data"]:
        print(f"  Claves en memoria: {list(mem_result['data'].keys())[:5]}...")
    
    print("\n=== REPORTE FINAL ===")
    report = hunter.generate_report()
    print(f"  Vulnerabilidades totales: {report['vulnerabilities_found']}")
    print(f"  Memoria comprometida: {report['memory_attack_success']}")
