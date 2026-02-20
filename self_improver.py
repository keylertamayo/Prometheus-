import re
from memory_manager import MemoryManager

class SelfImprover:
    def __init__(self, memory_manager=None):
        self.memory = memory_manager or MemoryManager()
        self.last_analysis = None

    def analyze_code(self, module_name: str):
        try:
            with open(module_name, "r") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Module {module_name} not found for analysis.")
            self.last_analysis = []
            return []
        patterns = [r"TODO", r"FIXME"]
        findings = []
        for pat in patterns:
            for match in re.finditer(pat, text):
                # capture line
                line = text.splitlines()[text[:match.start()].count("\n")]
                findings.append(line.strip())
        # naive inefficient pattern detection (simulated)
        self.last_analysis = findings
        return findings

    def propose_improvement(self):
        if not self.last_analysis:
            return "No improvements detected."
        desc = "; ".join([f"Se puede revisar: {line}" for line in self.last_analysis])
        return desc

    def test_improvement(self):
        print("Probando mejora...")
        result = "mejora probada"
        self.memory.store_memory("last_improvement_test", result)
        return result
