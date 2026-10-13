import os
import socket
import sys
import threading
import time
import webbrowser

from streamlit.web import cli as stcli


HOST = "127.0.0.1"
PORT = 8501


def get_app_path():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "app.py")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")


def wait_for_port(host, port, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def open_browser_when_ready():
    if wait_for_port(HOST, PORT):
        webbrowser.open(f"http://{HOST}:{PORT}")


def main():
    app_path = get_app_path()

    threading.Thread(
        target=open_browser_when_ready,
        daemon=True,
    ).start()

    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        f"--server.address={HOST}",
        f"--server.port={PORT}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]

    stcli.main()


if __name__ == "__main__":
    main()
