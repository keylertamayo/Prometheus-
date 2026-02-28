from evolution_engine import EvolutionEngine
import base64, os

if __name__ == '__main__':
    engine = EvolutionEngine(generations=1)
    # Force DNA with memory_encryption True
    dna = {
        "generation": 0,
        "aggressiveness": 0.5,
        "learning_rate": 0.5,
        "memory_encryption": True,
        "sandbox_hardening": True
    }
    # Generate key and pass as bytes
    memory_key = base64.urlsafe_b64encode(os.urandom(32))
    print("Generated MEMORY_KEY (preview):", memory_key.decode()[:8] + "...")
    fitness = engine.run_generation(dna)
    print("Generation finished. fitness=", fitness)
