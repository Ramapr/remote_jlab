from fabric import Connection
import time
import os
import webbrowser
from dotenv import load_dotenv


# Конфигурация
load_dotenv('.env')  

PC_HOST = os.getenv("PC_HOST")
PC_USER = os.getenv("PC_USER")
VENV_PATH = os.getenv("VENV_PATH")
TMUX_SESSION_NAME = os.getenv("TMUX_SESSION_NAME")      
PORT = os.getenv("PORT")


def capture_token(c):
    cmd = "tmux capture-pane -p -t jupyter_session_base | grep -Eo 'http://(127.0.0.1|localhost):[0-9]+/\\S+'"
    return c.run(cmd, hide=True, warn=True)


def fake_restart(c, exit=False):
    c.run(f"tmux send-keys -t {TMUX_SESSION_NAME} C-c", hide=True, warn=True)
    cmd = 'y' if exit else 'n'
    c.run(f"tmux send-keys -t {TMUX_SESSION_NAME} {cmd} Enter", hide=True, warn=True)
  

def get_jupyter_url(c):
    """Получает URL запущенного Jupyter Lab из tmux"""
    result_check = c.run(f"tmux list-sessions | grep {TMUX_SESSION_NAME}", hide=True, warn=True)
    
    if result_check.failed:
        print("⚠️ Jupyter tmux session not found!")
        return None
      
    for i in range(2):
        result = capture_token(c)
        if not result.failed or result.stdout.strip():
            return result.stdout.strip()
        else: 
            print(f"⚠️ No Jupyter URL found in tmux session no={i+1}!"	
            print("Try simulate restart!")
            fake_restart(c) 
    
    return None

def start_jupyter(c):
    """Запускает Jupyter Lab в новой tmux-сессии"""
    print("🔄 Запускаю Jupyter Lab...")
    c.run(f"tmux new-session -d -s {TMUX_SESSION_NAME} 'source {VENV_PATH} && jupyter lab --no-browser --port {PORT}'")
    time.sleep(3)  
    # Ждём, чтобы сервер успел стартануть
    return get_jupyter_url(c)

def connect_or_start_jupyter():
    """Подключается к Jupyter Lab, если он запущен, иначе запускает его"""
    with Connection(host=PC_HOST, user=PC_USER) as c:
        # Проверяем, запущена ли tmux-сессия
        result = c.run(f"tmux has-session -t {TMUX_SESSION_NAME}", warn=True)
        if result.ok:
            print("✅ Jupyter Lab уже запущен. Подключаюсь...")
            jupyter_url = get_jupyter_url(c)
        else:
            jupyter_url = start_jupyter(c)
    
    if jupyter_url:
        print(f"🔜 Открываю {jupyter_url}")
        webbrowser.open(jupyter_url)
    else:
        print("⚠️ Не удалось получить URL Jupyter Lab!")
        print(jupyter_url)


if __name__ == "__main__":
    connect_or_start_jupyter()
