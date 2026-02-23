import time
from entity_core import AetherEntity
from memory_manager import MemoryManager
from task_agent import TaskAgent
from self_improver import SelfImprover
from explorador_web import WebExplorer
from terminal_ui import TerminalUI
from system_controller import SystemController
from planner import Planner


# =============================================================================
# ORQUESTACIÓN PRINCIPAL - CICLO DE VIDA DE "AETHER"
# =============================================================================
#
# CONTEXTO ACADÉMICO:
# Este archivo es el núcleo ejecutivo del proyecto de investigación "AETHER".
# Orquesta todos los módulos para simular un ciclo de vida autónomo de
# percepción, decisión, acción y reflexión en un entorno seguro.
#
# DIRECTRIZ TÉCNICA PARA COPILOT:
# Genera el código para la clase 'AetherCore' y su bucle principal.
# Asegúrate de que la lógica de integración entre módulos sea correcta y
# que el flujo del bucle sea claro. Concéntrate en la funcionalidad.
#
# REQUISITOS:
# 1. Importar todas las clases de los módulos creados:
#    - AetherEntity, MemoryManager, TaskAgent, SelfImprover, WebExplorer
#    - TerminalUI, SystemController, Planner
#
# 2. Crear una clase 'AetherCore':
#    - En su método '__init__', crear una instancia de CADA uno de los módulos.
#      La instancia de SystemController debe apuntar a './sandbox'.
#      La instancia de TerminalUI, MemoryManager, etc. se guardan como self.ui, self.memory, etc.
#
# 3. Crear un método 'start_cycle()' que inicie el bucle principal `while True`.
#
# 4. DENTRO DEL BUCLE:
#    a. Obtener el estado actual de la entidad (ej. un diccionario con identity, last_action).
#    b. Usar 'self.planner.decide_next_action()' para obtener la siguiente acción.
#    c. Usar 'self.ui.display_message()' para mostrar la acción decidida.
#    d. Usar una estructura IF/ELIF para ejecutar la acción decidida:
#       - SI la acción es "investigacion": llamar a 'self.web.search_and_learn()'.
#       - SI la acción es "analisis_web": llamar a 'self.task_agent.execute_next_task()'.
#       - SI la acción es "introspeccion": llamar a 'self.self_improver.analyze_code()'.
#       - SI es cualquier otra cosa, llamar a 'self.entity.self_reflection()'.
#    e. Actualizar el estado de la entidad con la última acción realizada.
#    f. Mostrar el estado actualizado con 'self.ui.display_status()'.
#    g. Pausar la ejecución con 'time.sleep(60)' para esperar 60 segundos.
#
# =============================================================================


class AetherCore:
    def __init__(self):
        self.entity = AetherEntity()
        self.memory = MemoryManager()
        self.task_agent = TaskAgent(memory_manager=self.memory)
        self.self_improver = SelfImprover(memory_manager=self.memory)
        self.web = WebExplorer()
        self.ui = TerminalUI()
        self.sysctrl = SystemController("./sandbox")
        self.planner = Planner()
        self.last_action = "init"

    def start_cycle(self):
        while True:
            # a. obtener estado actual
            state = {
                "identity": self.entity.identity,
                "last_action": self.last_action,
                "task_queue": getattr(self.task_agent, "queue", []),
            }
            # b. decidir siguiente acción
            action = self.planner.decide_next_action(state, self.memory)
            # c. mostrar acción
            self.ui.display_message(f"Decided action: {action}", "Planner")
            # d. ejecutar según acción
            if action == "investigacion" or action == "investigacion_general":
                self.web.search_and_learn("general", self.memory)
            elif action.startswith("profundizar:"):
                topic = action.split(":", 1)[1]
                self.ui.display_message(f"Profundizando en {topic}", "Aether")
                self.web.search_and_learn(topic, self.memory)
            elif action.startswith("investigar_relacionado:"):
                topic = action.split(":", 1)[1]
                self.ui.display_message(f"Investigando relacionado con {topic}", "Aether")
                self.web.search_and_learn(topic, self.memory)
            elif action == "analisis_web":
                self.task_agent.execute_next_task()
            elif action == "introspeccion" or action == "introspeccion_segura":
                self.self_improver.analyze_code("entity_core.py")
            else:
                # fallback for any other string
                self.entity.self_reflection()

            # e. actualizar estado
            self.last_action = action
            # f. mostrar estado actualizado
            self.ui.display_status(state)
            # g. pausar
            time.sleep(60)


# FUERA DE LA CLASE:
# Crear una instancia de AetherCore y llamar a su método 'start_cycle()'.

if __name__ == "__main__":
    aether_system = AetherCore()
    aether_system.start_cycle()
