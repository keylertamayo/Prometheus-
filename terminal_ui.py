import datetime

class TerminalUI:
    def __init__(self):
        pass

    def display_message(self, message: str, source: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{source}] {timestamp} -> {message}")

    def get_user_command(self):
        try:
            cmd = input("> ")
        except EOFError:
            cmd = ""
        except Exception as e:
            print(f"Error reading input: {e}")
            cmd = ""
        return cmd.strip()

    def display_status(self, entity_status: dict):
        # expect keys like identity, objective, last_action
        print("--- ENTITY STATUS ---")
        for key in ["identity", "objective", "last_action"]:
            if key in entity_status:
                print(f"{key.capitalize():12}: {entity_status[key]}")
        print("---------------------")
