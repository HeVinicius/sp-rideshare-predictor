import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SP_LAT = os.getenv("SP_LAT", "-23.5505")
SP_LON = os.getenv("SP_LON", "-46.6333")

def get_weather_sp():
    key = os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={SP_LAT}&lon={SP_LON}&appid={key}&units=metric&lang=pt_br"
    r = requests.get(url, timeout=10)
    return r.json()

def get_traffic_tomtom():
    try:
        key = os.getenv("TOMTOM_API_KEY")
        # Busca fluxo de trânsito ao redor do centro de SP
        url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={SP_LAT},{SP_LON}&key={key}"
        r = requests.get(url, timeout=10)
        data = r.json()

        if "flowSegmentData" in data:
            flow = data["flowSegmentData"]
            velocidade_atual = flow.get("currentSpeed", 0)
            velocidade_livre = flow.get("freeFlowSpeed", 1)
            confianca = flow.get("confidence", 0)

            # Percentual de lentidão (0% = trânsito livre, 100% = parado)
            percentual_lento = round((1 - velocidade_atual / velocidade_livre) * 100, 1)
            percentual_lento = max(0, percentual_lento)

            return {
                "velocidade_atual_kmh": velocidade_atual,
                "velocidade_livre_kmh": velocidade_livre,
                "percentual_lento": percentual_lento,
                "confianca": confianca,
                "fonte": "TomTom"
            }
        else:
            return {"percentual_lento": 0, "erro": str(data)}

    except Exception as e:
        return {"erro": str(e), "percentual_lento": 0}

def calcular_score(weather, traffic):
    score = 100

    # Penaliza por chuva
    if "weather" in weather:
        cond_id = weather["weather"][0]["id"]
        if cond_id < 300:
            score -= 40  # tempestade
        elif cond_id < 600:
            score -= 25  # chuva
        elif cond_id < 700:
            score -= 10  # garoa

    # Penaliza por trânsito
    pct = traffic.get("percentual_lento", 0)
    if pct > 50:
        score -= 35
    elif pct > 30:
        score -= 20
    elif pct > 15:
        score -= 10

    # Penaliza por horário de pico SP
    hora = datetime.now().hour
    if hora in range(7, 10) or hora in range(17, 21):
        score -= 20

    return max(0, min(100, score))

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

    os.makedirs("data/raw", exist_ok=True)
    fname = f"data/raw/snap_{now.strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Coletado: {now.strftime('%d/%m %H:%M')} | Score: {score} | Velocidade: {traffic.get('velocidade_atual_kmh', '?')} km/h | Lento: {traffic.get('percentual_lento', 0)}%")

if __name__ == "__main__":
    collect_snapshot()