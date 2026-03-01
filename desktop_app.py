import sys
import time
import threading
import subprocess
import socket
import webview
import logging

def is_port_in_use(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    except socket.error:
        return False

def start_streamlit():
    try:
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)

def main():
    try:
        t = threading.Thread(target=start_streamlit, daemon=True)
        t.start()

        timeout = 30
        start_time = time.time()
        
        while not is_port_in_use(8501):
            if time.time() - start_time > timeout:
                logging.error("Timeout")
                sys.exit(1)
            time.sleep(0.5)

        webview.create_window(
            'Job Search Tracker Dashboard', 
            'http://localhost:8501', 
            width=1280, 
            height=800
        )
        webview.start()
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    main()