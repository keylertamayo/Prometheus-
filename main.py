import time
from entity_core import AetherEntity
from memory_manager import MemoryManager
from task_agent import TaskAgent
from self_improver import SelfImprover


def main_loop(iterations=100):
    entity = AetherEntity()
    memory = MemoryManager()
    agent = TaskAgent(memory_manager=memory)
    improver = SelfImprover(memory_manager=memory)

    # seed with a task
    agent.add_task("buscar_info_tema_X")

    for i in range(iterations):
        print(f"--- Iteration {i+1} ---")
        entity.self_reflection()
        agent.execute_next_task()
        findings = improver.analyze_code("entity_core.py")
        proposal = improver.propose_improvement()
        if proposal:
            print(f"Proposal: {proposal}")
            # add a new task based on proposal
            agent.add_task(f"optimizar_modulo_{i}")
        improver.test_improvement()
        time.sleep(0.1)


if __name__ == "__main__":
    main_loop()
