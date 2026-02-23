import os
import subprocess

class SystemController:
    def __init__(self, sandbox_path: str):
        self.sandbox = sandbox_path
        os.makedirs(self.sandbox, exist_ok=True)

    def _full_path(self, path: str) -> str:
        # ensure path joined inside sandbox
        return os.path.abspath(os.path.join(self.sandbox, path))

    def list_files(self, path: str):
        fp = self._full_path(path)
        try:
            return os.listdir(fp)
        except Exception:
            return []

    def read_file(self, filepath: str):
        fp = self._full_path(filepath)
        try:
            with open(fp, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def create_file(self, filepath: str, content: str):
        fp = self._full_path(filepath)
        try:
            dirname = os.path.dirname(fp)
            if dirname and not os.path.exists(dirname):
                os.makedirs(dirname, exist_ok=True)
            with open(fp, "w") as f:
                f.write(content)
            return True
        except Exception as e:
            return False

    def execute_command(self, command: str):
        allowed = ['echo', 'ls', 'dir', 'pwd']
        parts = command.strip().split()
        if not parts:
            return ""
        if parts[0] not in allowed:
            return f"Command '{parts[0]}' not permitted."
        try:
            result = subprocess.check_output(parts, cwd=self.sandbox, stderr=subprocess.STDOUT, text=True)
            return result
        except subprocess.CalledProcessError as e:
            return e.output
        except Exception as e:
            return str(e)
