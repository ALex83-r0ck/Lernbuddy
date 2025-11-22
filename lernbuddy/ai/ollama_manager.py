import subprocess
import socket
import psutil


class OllamaManager:
    def __init__(self):
        self.process = None
        self.port = 11434

    def is_port_open(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("127.0.0.1", self.port))
        sock.close()
        return result == 0

    def start(self):
        # läuft bereits – nichts tun
        if self.is_port_open():
            print("Ollama läuft bereits.")
            return

        # falls alter Prozess hängt → killen
        self.kill_port_processes()

        print("Starte Ollama...")
        self.process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def kill_port_processes(self):
        for proc in psutil.process_iter(["pid", "name", "connections"]):
            for c in proc.info.get("connections", []):
                if c.laddr.port == self.port:
                    print(f"Beende hängenden Prozess: {proc.info['pid']}")
                    proc.kill()

    def stop(self):
        if self.process:
            print("Beende Ollama (App Exit)...")
            self.process.terminate()
            self.process = None
        else:
            # Wenn extern gestartet wurde → trotzdem Port freigeben
            self.kill_port_processes()
