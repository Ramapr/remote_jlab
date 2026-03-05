from fabric import Connection
import time
import os
import webbrowser
from dotenv import load_dotenv
import json


load_dotenv('.env')  

PC_HOST = os.getenv("PC_HOST")
PC_USER = os.getenv("PC_USER")
VENV_PATH = os.getenv("VENV_PATH")
TMUX_SESSION_NAME = os.getenv("TMUX_SESSION_NAME")      
PORT = os.getenv("PORT")
FILENAME = os.getenv("FILENAME")


def read_from_cache() -> str:
    with open(FILENAME, 'r') as f:
        data = json.read(f)
    return data['token']

def write_to_cache(s):
    with open(FILENAME, 'w') as f:
        json.dump({'token': s}, f, indent=4)

def capture_token(c):
    # cmd = f"tmux capture-pane -p -t {TMUX_SESSION_NAME} -J | grep -Eo 'http://(127.0.0.1|localhost):[0-9]+/\\S+'"
    cmd = f"tmux capture-pane -p -t {TMUX_SESSION_NAME} -J | grep -Eo 'http://(localhost):[0-9]+/\\S+'"
    return c.run(cmd, hide=True, warn=True)

# def fake_restart(c, exit=False):
#     c.run(f"tmux send-keys -t {TMUX_SESSION_NAME} C-c", hide=True, warn=True)
#     cmd = 'y' if exit else 'n'
#     c.run(f"tmux send-keys -t {TMUX_SESSION_NAME} {cmd} Enter", hide=True, warn=True)

def find_session(c):
    check = f"tmux list-sessions | grep {TMUX_SESSION_NAME}"
    return c.run(check, hide=True, warn=True)
    
def get_jupyter_url(c):
    """Получает URL запущенного Jupyter Lab из tmux"""
    result_check = find_session(c)
    if result_check.failed:
        print("⚠️ Jupyter tmux session not found!")
        return None
    result = capture_token(c)
    if not result.failed or result.stdout.strip():
        urls = result.stdout.strip()
        return urls.split('\n')[0] if '\n' in urls else urls 
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
        result = c.run(f"tmux has-session -t {TMUX_SESSION_NAME}", warn=True)
        if result.ok:
            print("✅ Jupyter Lab уже запущен. Подключаюсь...")
            jupyter_url = get_jupyter_url(c)
        else:
            print("🔄 Запускаю Jupyter Lab...")
            jupyter_url = start_jupyter(c) # may return more than 1
            if jupyter_url:
                write_to_cache(jupyter_url)

    # url = read_from_cache() if jupyter_url is None else jupyter_url
    # if url :
    #     print(f"🔜 Открываю {jupyter_url}")
    #     webbrowser.open(jupyter_url)
    # else :
    if jupyter_url:
        print(f"🔜 Открываю {jupyter_url}")
        webbrowser.open(jupyter_url)
    elif jupyter_url is None:
        print(f"READ TOKEN FROM CACHE")
        token = read_from_cache()
        print(f"🔜 Открываю {token}")
        webbrowser.open(token)
    else:
        print("⚠️ Не удалось получить URL Jupyter Lab!")


if __name__ == "__main__":
    connect_or_start_jupyter()
