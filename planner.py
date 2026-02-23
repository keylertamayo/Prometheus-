class Planner:
    def __init__(self):
        # La lista de posibles tareas puede ser más dinámica ahora.
        self.possible_tasks = ["investigacion", "analisis", "introspeccion"]

    def decide_next_action(self, entity_status: dict, memory_manager_instance):
        """Decide the next action based on entity status and, crucially, its past experiences stored in memory.
        Este método es adaptativo y utiliza la información de memoria para influir en la elección.
        """
        # obtener memoria completa
        mem = {}
        try:
            mem = memory_manager_instance.recall_all()
        except Exception:
            if hasattr(memory_manager_instance, '_load'):
                mem = memory_manager_instance._load()

        # contar temas de web_info en las claves
        topic_counts = {}
        for key in mem.keys():
            if key.startswith('web_info_'):
                parts = key.split('_')
                if len(parts) >= 3:
                    topic = parts[2]
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
        dominant = None
        if topic_counts:
            dominant = max(topic_counts, key=lambda t: topic_counts[t])
            counts = list(topic_counts.values())
            if counts.count(topic_counts[dominant]) > 1:
                dominant = None

        # regla de evitación: errores en memoria
        for k, v in mem.items():
            if 'error' in k.lower() or (isinstance(v, str) and 'error' in v.lower()):
                return 'introspeccion_segura'

        # regla de especialización
        if dominant:
            return f'profundizar:{dominant}'

        # regla de curiosidad
        if topic_counts:
            frequent = max(topic_counts, key=lambda t: topic_counts[t])
            return f'investigar_relacionado:{frequent}'

        # regla por defecto
        return 'investigacion_general'
