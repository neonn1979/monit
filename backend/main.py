from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pysnmp.hlapi import *
from datetime import datetime
import logging
import requests
import threading
import time

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка логирования
logging.basicConfig(filename='log.txt', level=logging.INFO)

# Telegram Bot
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# SNMP-опрос
def snmp_get(ip, community, oid):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    if errorIndication:
        return None
    elif errorStatus:
        return None
    else:
        for varBind in varBinds:
            return str(varBind[1])

# Периодический опрос
def poll_devices():
    devices = [
        {"ip": "192.168.1.1", "community": "public", "oid": "1.3.6.1.2.1.1.3.0"}  # sysUpTime
    ]
    while True:
        for dev in devices:
            result = snmp_get(dev["ip"], dev["community"], dev["oid"])
            status = "online" if result else "offline"
            log_msg = f"{datetime.now()} - {dev['ip']} - {status}"
            logging.info(log_msg)
            if status == "offline":
                send_telegram(f"Устройство {dev['ip']} недоступно!")
        time.sleep(60)  # Опрос раз в минуту

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        logging.error(f"Ошибка отправки Telegram: {e}")

# Запуск опроса в фоновом потоке
threading.Thread(target=poll_devices, daemon=True).start()

@app.get("/api/status")
def get_status():
    return JSONResponse({
        "device": "192.168.1.1",
        "status": "online",
        "uptime": snmp_get("192.168.1.1", "public", "1.3.6.1.2.1.1.3.0") or "n/a"
    })