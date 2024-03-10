import threading
import subprocess
import time


def run_server():
    subprocess.run(['python', 'server.py'])


def run_client():
    subprocess.run(['python', 'client.py'])


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    time.sleep(2)
    run_client()
