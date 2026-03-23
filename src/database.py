import mysql.connector
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "vaiagora_sp")
    )

def salvar_snapshot(data: dict):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        weather = data.get("weather", {})
        traffic = data.get("traffic", {})

        temp = weather.get("main", {}).get("temp", None)
        umidade = weather.get("main", {}).get("humidity", None)
        clima_desc = weather.get("weather", [{}])[0].get("description", None)
        clima_id = weather.get("weather", [{}])[0].get("id", None)
        chuva = clima_id < 700 if clima_id else False

        sql = """
            INSERT INTO snapshots
            (timestamp, hour, weekday, score, temp, umidade, clima_desc,
             clima_id, chuva, velocidade_atual, velocidade_livre, percentual_lento)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            data.get("timestamp", datetime.now().isoformat()),
            data.get("hour"),
            data.get("weekday"),
            data.get("score"),
            temp, umidade, clima_desc, clima_id, chuva,
            traffic.get("velocidade_atual_kmh"),
            traffic.get("velocidade_livre_kmh"),
            traffic.get("percentual_lento")
        )

        cursor.execute(sql, valores)
        conn.commit()
        print(f"✓ Snapshot salvo no banco!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar snapshot: {e}")

def salvar_rota(rota: dict):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO rotas
            (origem, destino, lat_orig, lon_orig, lat_dest, lon_dest,
             distancia_km, tempo_min, custo_min, custo_max, score_momento)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            rota.get("origem"), rota.get("destino"),
            rota.get("lat_orig"), rota.get("lon_orig"),
            rota.get("lat_dest"), rota.get("lon_dest"),
            rota.get("distancia_km"), rota.get("tempo_min"),
            rota.get("custo_min"), rota.get("custo_max"),
            rota.get("score_momento")
        )

        cursor.execute(sql, valores)
        conn.commit()
        print(f"✓ Rota salva no banco!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar rota: {e}")

def salvar_clique_mapa(clique: dict):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO cliques_mapa
            (lat, lon, velocidade_atual, velocidade_livre,
             percentual_lento, status_transito)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (
            clique.get("lat"), clique.get("lng"),
            clique.get("vel_atual"), clique.get("vel_livre"),
            clique.get("pct_lento"), clique.get("status")
        )

        cursor.execute(sql, valores)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar clique: {e}")

def buscar_ultimos_snapshots(limit=50):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM snapshots ORDER BY timestamp DESC LIMIT {limit}")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Erro ao buscar snapshots: {e}")
        return []

def buscar_ultimo_snapshot():
    rows = buscar_ultimos_snapshots(limit=1)
    return rows[0] if rows else None

def buscar_historico_rotas(limit=20):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM rotas ORDER BY created_at DESC LIMIT {limit}")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Erro ao buscar rotas: {e}")
        return []