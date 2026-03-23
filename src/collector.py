import sys
import os

# 🔥 GARANTE QUE O PYTHON ENXERGUE O PROJETO
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# 🔥 IMPORT CORRETO DO DATABASE
from src.database import salvar_snapshot

load_dotenv()

SP_LAT = os.getenv("SP_LAT", "-23.5505")
SP_LON = os.getenv("SP_LON", "-46.6333")

# =========================
# 🌤️ CLIMA
# =========================
def get_weather_sp():
    key = os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={SP_LAT}&lon={SP_LON}&appid={key}&units=metric&lang=pt_br"
    r = requests.get(url, timeout=10)
    return r.json()

# =========================
# 🚦 TRÂNSITO
# =========================
def get_traffic_tomtom():
    try:
        key = os.getenv("TOMTOM_API_KEY")
        url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={SP_LAT},{SP_LON}&key={key}"
        r = requests.get(url, timeout=10)
        data = r.json()

        if "flowSegmentData" in data:
            flow = data["flowSegmentData"]
            vel_atual = flow.get("currentSpeed", 0)
            vel_livre = flow.get("freeFlowSpeed", 1)
            pct_lento = max(0, round((1 - vel_atual / vel_livre) * 100, 1))

            return {
                "velocidade_atual_kmh": vel_atual,
                "velocidade_livre_kmh": vel_livre,
                "percentual_lento": pct_lento,
                "confianca": flow.get("confidence", 0),
                "fonte": "TomTom"
            }

        return {
            "percentual_lento": 0,
            "velocidade_atual_kmh": 0,
            "velocidade_livre_kmh": 0
        }

    except Exception as e:
        return {
            "erro": str(e),
            "percentual_lento": 0,
            "velocidade_atual_kmh": 0,
            "velocidade_livre_kmh": 0
        }

# =========================
# 🧠 SCORE
# =========================
def calcular_score(weather, traffic):
    score = 100

    if "weather" in weather:
        cond_id = weather["weather"][0]["id"]

        if cond_id < 300:
            score -= 40
        elif cond_id < 600:
            score -= 25
        elif cond_id < 700:
            score -= 10

    pct = traffic.get("percentual_lento", 0)

    if pct > 50:
        score -= 35
    elif pct > 30:
        score -= 20
    elif pct > 15:
        score -= 10

    hora = datetime.now().hour

    if hora in range(7, 10) or hora in range(17, 21):
        score -= 20

    return max(0, min(100, score))

# =========================
# 📦 COLETA
# =========================
def collect_snapshot():
    now = datetime.now()

    try:
        weather = get_weather_sp()
    except Exception as e:
        print(f"Erro clima: {e}")
        weather = {}

    traffic = get_traffic_tomtom()
    score = calcular_score(weather, traffic)

    data = {
        "timestamp": now.isoformat(),
        "hour": now.hour,
        "weekday": now.weekday(),
        "score": score,
        "weather": weather,
        "traffic": traffic
    }

    # 💾 Salva JSON local
    os.makedirs("data/raw", exist_ok=True)
    fname = f"data/raw/snap_{now.strftime('%Y%m%d_%H%M')}.json"

    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 💾 Salva no banco
    salvar_snapshot(data)

    print(
        f"Coletado: {now.strftime('%d/%m %H:%M')} | "
        f"Score: {score} | "
        f"Velocidade: {traffic.get('velocidade_atual_kmh', 0)} km/h | "
        f"Lento: {traffic.get('percentual_lento', 0)}%"
    )

# =========================
# ▶️ EXECUÇÃO DIRETA
# =========================
if __name__ == "__main__":
    collect_snapshot()