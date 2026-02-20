import time

class AetherEntity:
    def __init__(self):
        self.identity = "Aether"
        self.objective = "Optimize self and learn"
        self.logfile = "aether_actions.log"

    def self_reflection(self):
        print("Aether: Analizando mi estado actual...")

    def log_action(self, action: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{timestamp} - {action}\n"
        with open(self.logfile, "a") as f:
            f.write(entry)
