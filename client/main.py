import websocket
import json
import time
import os
import platform
import uuid
import threading

SERVER_URL = "ws://YOUR_SERVER_IP:3000"
DEVICE_ID = str(uuid.uuid4())[:8]

def get_system_info():
    return {
        "os": platform.system(),
        "hostname": platform.node()
    }

def shutdown_computer(delay_seconds=0):
    if delay_seconds > 0:
        time.sleep(delay_seconds)
    
    system = platform.system()
    if system == "Windows":
        os.system("shutdown /s /t 0")
    elif system == "Linux" or system == "Darwin":
        os.system("shutdown -h now")

def schedule_shutdown(seconds):
    print(f"Scheduling shutdown in {seconds} seconds")
    timer = threading.Timer(seconds, shutdown_computer)
    timer.start()

def on_message(ws, message):
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
            if platform.system() == "Windows":
                os.system("shutdown /a")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed, reconnecting in 5 seconds...")
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
    ws = websocket.WebSocketApp(
        SERVER_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    ws.run_forever()

if __name__ == "__main__":
    print(f"Starting client with device ID: {DEVICE_ID}")
    print(f"Connecting to server: {SERVER_URL}")
    connect()