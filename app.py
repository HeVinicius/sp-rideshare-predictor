import sys
import os

# 🔥 GARANTE QUE O PYTHON ENXERGUE A PASTA DO PROJETO
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# 🔥 (EXTRA) garante acesso à pasta src explicitamente
sys.path.append(os.path.join(BASE_DIR, "src"))

# IMPORTS
import streamlit as st
import json
import folium
import requests
from streamlit_folium import st_folium
from datetime import datetime
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

# 🔥 IMPORTS INTERNOS (depois do path!)
from src.collector import get_weather_sp, get_traffic_tomtom, calcular_score
from src.database import (
    salvar_snapshot, salvar_rota, salvar_clique_mapa,
    buscar_ultimos_snapshots, buscar_ultimo_snapshot,
    buscar_historico_rotas, get_connection
)

# LOAD ENV
load_dotenv()


st.set_page_config(page_title="VaiAgora SP", layout="wide", page_icon="🚗")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] {
    background-color: #080c10 !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 2rem !important;}
.vai-title { font-family: 'Bebas Neue', sans-serif; font-size: 64px; line-height: 0.95; letter-spacing: 2px; }
.vai-title span { color: #f5c842; }
.live-tag {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(245,200,66,0.1); border: 1px solid rgba(245,200,66,0.2);
    color: #f5c842; font-size: 11px; font-weight: 500; letter-spacing: 2px;
    padding: 6px 14px; border-radius: 100px; margin-bottom: 32px;
}
.score-card {
    background: #0e1419; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 40px; text-align: center; margin-bottom: 20px;
    position: relative; overflow: hidden;
}
.score-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #f5c842, transparent);
}
.score-number { font-family: 'Bebas Neue', sans-serif; font-size: 100px; line-height: 1; }
.score-msg { font-size: 20px; margin-top: 8px; }
.snap-card {
    background: #0e1419; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;
    font-size: 13px; color: #6b7280; font-family: monospace;
}
.alerta {
    background: rgba(255,107,53,0.08); border-left: 3px solid #ff6b35;
    border-radius: 0 10px 10px 0; padding: 14px 18px;
    font-size: 14px; margin-top: 16px; color: #e8e4dc;
}
.rota-card {
    background: #0e1419; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 24px; margin-top: 16px;
}
.stButton > button {
    background: #f5c842 !important; color: #080c10 !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important;
    font-size: 15px !important; padding: 12px 32px !important;
    border-radius: 8px !important; border: none !important; width: 100%;
}
.stButton > button:hover { background: #f7d35a !important; }
hr { border-color: rgba(255,255,255,0.07) !important; }
[data-testid="metric-container"] {
    background: #0e1419; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 16px 20px;
}
[data-testid="stMetricLabel"] { color: #6b7280 !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: #e8e4dc !important; }
.stTextInput > div > div > input {
    background: #0e1419 !important; color: #e8e4dc !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important; font-size: 14px !important;
}
.stSelectbox > div > div {
    background: #0e1419 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("""
<div class='live-tag'>● São Paulo · Tempo Real · IA</div>
<div class='vai-title'>VAI<span>AGORA</span></div>
<p style='color:#6b7280; font-size:16px; margin-bottom:32px'>
    Saiba o momento exato de chamar seu Uber ou 99 em SP
</p>
""", unsafe_allow_html=True)

st.divider()

# ANÁLISE
col_btn, _ = st.columns([1, 3])
with col_btn:
    analisar = st.button("Analisar agora")

if "analise" not in st.session_state:
    st.session_state.analise = None

if analisar:
    with st.spinner("Consultando clima e trânsito de SP..."):
        try:
            weather = get_weather_sp()
            traffic = get_traffic_tomtom()
            score = calcular_score(weather, traffic)
            st.session_state.analise = {"weather": weather, "traffic": traffic, "score": score}

            # Salva no banco
            salvar_snapshot({
                "timestamp": datetime.now().isoformat(),
                "hour": datetime.now().hour,
                "weekday": datetime.now().weekday(),
                "score": score,
                "weather": weather,
                "traffic": traffic
            })
        except Exception as e:
            st.error(f"Erro: {e}")

if st.session_state.analise:
    score = st.session_state.analise["score"]
    weather = st.session_state.analise["weather"]
    traffic = st.session_state.analise["traffic"]

    if score >= 75:
        cor_hex, icone, msg = "#4ade80", "🟢", "Ótimo momento para chamar!"
    elif score >= 50:
        cor_hex, icone, msg = "#f5c842", "🟡", "Momento razoável, pode chamar."
    else:
        cor_hex, icone, msg = "#ff6b35", "🔴", "Evite agora! Trânsito ou chuva."

    st.markdown(f"""
    <div class='score-card'>
        <div style='font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#6b7280;margin-bottom:12px'>Score do momento</div>
        <div class='score-number' style='color:{cor_hex};text-shadow:0 0 40px {cor_hex}40'>{score}</div>
        <div class='score-msg'>{icone} {msg}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    if "main" in weather:
        col1.metric("🌡️ Temperatura", f"{weather['main']['temp']:.1f}°C")
        col2.metric("💧 Umidade", f"{weather['main']['humidity']}%")
        col3.metric("🌤️ Clima", weather['weather'][0]['description'].capitalize())
    col4.metric("🚦 Velocidade atual", f"{traffic.get('velocidade_atual_kmh', 0)} km/h")

    hora = datetime.now().hour
    if hora in range(7, 10):
        st.markdown("<div class='alerta'>⚠️ Horário de pico da manhã em SP (7h–9h). Considere esperar.</div>", unsafe_allow_html=True)
    elif hora in range(17, 21):
        st.markdown("<div class='alerta'>⚠️ Horário de pico da tarde em SP (17h–20h). Considere esperar.</div>", unsafe_allow_html=True)

st.divider()

# CALCULADORA DE ROTA
st.markdown("<p style='font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#f5c842'>Calculadora</p>", unsafe_allow_html=True)
st.markdown("<p style='font-family:Bebas Neue,sans-serif;font-size:32px;letter-spacing:1px'>SIMULAR MINHA CORRIDA</p>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;font-size:14px;margin-bottom:20px'>Digite origem e destino para estimar tempo e custo da corrida.</p>", unsafe_allow_html=True)

geo = Nominatim(user_agent="vaiagora_sp", timeout=5)

def buscar_sugestoes(texto):
    if len(texto) < 4:
        return []
    try:
        resultados = geo.geocode(f"{texto}, São Paulo, Brasil", exactly_one=False, limit=5, language="pt")
        return resultados if resultados else []
    except:
        return []

if "coord_orig" not in st.session_state:
    st.session_state.coord_orig = None
if "coord_dest" not in st.session_state:
    st.session_state.coord_dest = None
if "rota_resultado" not in st.session_state:
    st.session_state.rota_resultado = None

col_orig, col_dest = st.columns(2)

with col_orig:
    origem_texto = st.text_input("📍 Origem", placeholder="Ex: Av Paulista, 1000")
    if origem_texto and len(origem_texto) >= 4:
        sugestoes_orig = buscar_sugestoes(origem_texto)
        if sugestoes_orig:
            opcoes_orig = {r.address[:80]: r for r in sugestoes_orig}
            selecionada_orig = st.selectbox("Selecione a origem:", list(opcoes_orig.keys()), key="sel_orig")
            st.session_state.coord_orig = opcoes_orig[selecionada_orig]
        else:
            st.caption("Nenhuma sugestão encontrada.")

with col_dest:
    destino_texto = st.text_input("🏁 Destino", placeholder="Ex: Butantã, São Paulo")
    if destino_texto and len(destino_texto) >= 4:
        sugestoes_dest = buscar_sugestoes(destino_texto)
        if sugestoes_dest:
            opcoes_dest = {r.address[:80]: r for r in sugestoes_dest}
            selecionada_dest = st.selectbox("Selecione o destino:", list(opcoes_dest.keys()), key="sel_dest")
            st.session_state.coord_dest = opcoes_dest[selecionada_dest]
        else:
            st.caption("Nenhuma sugestão encontrada.")

col_calc, _ = st.columns([1, 3])
with col_calc:
    calcular = st.button("🚗 Calcular rota")

if calcular:
    loc_orig = st.session_state.coord_orig
    loc_dest = st.session_state.coord_dest

    if not loc_orig or not loc_dest:
        st.warning("⚠️ Selecione origem e destino antes de calcular.")
    else:
        with st.spinner("Calculando rota..."):
            try:
                url = (
                    f"http://router.project-osrm.org/route/v1/driving/"
                    f"{loc_orig.longitude},{loc_orig.latitude};"
                    f"{loc_dest.longitude},{loc_dest.latitude}"
                    f"?overview=full&geometries=geojson&steps=true"
                )
                r = requests.get(url, timeout=15)
                data = r.json()

                if data.get("code") == "Ok" and data.get("routes"):
                    rota = data["routes"][0]
                    distancia_km = round(rota["distance"] / 1000, 1)
                    tempo_min = round(rota["duration"] / 60)
                    coords_rota = rota["geometry"]["coordinates"]
                    pontos_rota = [[c[1], c[0]] for c in coords_rota]

                    instrucoes = []
                    for step in rota["legs"][0]["steps"]:
                        nome = step.get("name", "")
                        dist = round(step["distance"])
                        manobra = step.get("maneuver", {}).get("type", "")
                        if nome and dist > 20:
                            instrucoes.append(f"{manobra.replace('-', ' ').capitalize()} em {nome} ({dist}m)")

                    custo_min = round(5.00 + (distancia_km * 2.20) + (tempo_min * 0.35), 2)
                    custo_max = round(5.00 + (distancia_km * 3.20) + (tempo_min * 0.50), 2)

                    score_atual = st.session_state.analise["score"] if st.session_state.analise else 100
                    if score_atual < 50:
                        tempo_min = round(tempo_min * 1.4)
                        custo_min = round(custo_min * 1.3, 2)
                        custo_max = round(custo_max * 1.5, 2)

                    rota_data = {
                        "origem": loc_orig.address[:60],
                        "destino": loc_dest.address[:60],
                        "lat_orig": loc_orig.latitude,
                        "lon_orig": loc_orig.longitude,
                        "lat_dest": loc_dest.latitude,
                        "lon_dest": loc_dest.longitude,
                        "distancia_km": distancia_km,
                        "tempo_min": tempo_min,
                        "custo_min": custo_min,
                        "custo_max": custo_max,
                        "pontos_rota": pontos_rota,
                        "instrucoes": instrucoes[:8],
                        "score_momento": score_atual
                    }

                    st.session_state.rota_resultado = rota_data

                    # Salva rota no banco
                    salvar_rota(rota_data)

                else:
                    st.error("❌ Não foi possível calcular a rota.")

            except Exception as e:
                st.error(f"❌ Erro: {e}")

if st.session_state.rota_resultado:
    r = st.session_state.rota_resultado
    col_mapa_rota, col_info_rota = st.columns([3, 2])

    with col_mapa_rota:
        centro_lat = (r["lat_orig"] + r["lat_dest"]) / 2
        centro_lon = (r["lon_orig"] + r["lon_dest"]) / 2
        m_rota = folium.Map(location=[centro_lat, centro_lon], zoom_start=13, tiles="CartoDB dark_matter")
        folium.PolyLine(r["pontos_rota"], color="#f5c842", weight=5, opacity=0.9, tooltip="Rota sugerida").add_to(m_rota)
        folium.Marker(location=[r["lat_orig"], r["lon_orig"]], popup="📍 Origem", tooltip="📍 Origem", icon=folium.Icon(color="green", icon="play", prefix="fa")).add_to(m_rota)
        folium.Marker(location=[r["lat_dest"], r["lon_dest"]], popup="🏁 Destino", tooltip="🏁 Destino", icon=folium.Icon(color="red", icon="flag", prefix="fa")).add_to(m_rota)
        st_folium(m_rota, width=None, height=420)

    with col_info_rota:
        st.markdown(f"""
        <div class='rota-card'>
            <p style='font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#6b7280;margin-bottom:12px'>Resultado da rota</p>
            <p style='font-size:12px;color:#6b7280;margin-bottom:2px'>📍 {r['origem'][:55]}</p>
            <p style='font-size:12px;color:#6b7280;margin-bottom:20px'>🏁 {r['destino'][:55]}</p>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px'>
                <div style='background:#141c24;border-radius:10px;padding:14px'>
                    <div style='font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#6b7280;margin-bottom:2px'>Distância</div>
                    <div style='font-family:Bebas Neue,sans-serif;font-size:34px;color:#e8e4dc;line-height:1'>{r['distancia_km']}</div>
                    <div style='font-size:11px;color:#6b7280'>km</div>
                </div>
                <div style='background:#141c24;border-radius:10px;padding:14px'>
                    <div style='font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#6b7280;margin-bottom:2px'>Tempo estimado</div>
                    <div style='font-family:Bebas Neue,sans-serif;font-size:34px;color:#e8e4dc;line-height:1'>{r['tempo_min']}</div>
                    <div style='font-size:11px;color:#6b7280'>minutos</div>
                </div>
            </div>
            <div style='background:#141c24;border-radius:10px;padding:16px;margin-bottom:12px'>
                <div style='font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#6b7280;margin-bottom:6px'>Custo estimado</div>
                <div style='font-family:Bebas Neue,sans-serif;font-size:38px;color:#4ade80;line-height:1'>R$ {r['custo_min']:.0f} – {r['custo_max']:.0f}</div>
                <div style='font-size:11px;color:#6b7280;margin-top:4px'>Uber / 99 / InDrive — tarifa padrão SP</div>
            </div>
            <div style='font-size:11px;color:#6b7280;line-height:1.6'>💡 Valor pode variar com surge pricing, categoria e promoções.</div>
        </div>
        """, unsafe_allow_html=True)

        if r["instrucoes"]:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#f5c842;margin-bottom:10px'>Sugestão de rota</p>", unsafe_allow_html=True)
            for i, instrucao in enumerate(r["instrucoes"], 1):
                st.markdown(f"""
                <div style='background:#0e1419;border:1px solid rgba(255,255,255,0.05);border-radius:8px;padding:10px 14px;margin-bottom:6px;font-size:12px;color:#6b7280'>
                    <span style='color:#f5c842;font-weight:600;margin-right:8px'>{i}.</span>{instrucao}
                </div>
                """, unsafe_allow_html=True)

st.divider()

# MAPA INTERATIVO
st.markdown("<p style='font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#f5c842'>Mapa interativo</p>", unsafe_allow_html=True)
st.markdown("<p style='font-family:Bebas Neue,sans-serif;font-size:32px;letter-spacing:1px'>CLIQUE NO MAPA PARA VER O TRÂNSITO</p>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;font-size:14px;margin-bottom:20px'>Clique em qualquer ponto de São Paulo para consultar o trânsito em tempo real.</p>", unsafe_allow_html=True)

col_mapa, col_resultado = st.columns([3, 2])

with col_mapa:
    m = folium.Map(location=[-23.5505, -46.6333], zoom_start=12, tiles="CartoDB dark_matter")
    if "ultimo_clique" in st.session_state and st.session_state.ultimo_clique:
        lat = st.session_state.ultimo_clique["lat"]
        lon = st.session_state.ultimo_clique["lng"]
        cor = st.session_state.get("clique_resultado", {}).get("cor", "#f5c842") if st.session_state.get("clique_resultado") else "#f5c842"
        folium.CircleMarker(location=[lat, lon], radius=16, color=cor, fill=True, fill_color=cor, fill_opacity=0.8, tooltip="📍 Ponto selecionado").add_to(m)

    mapa_data = st_folium(m, width=None, height=480, returned_objects=["last_clicked"])

    if mapa_data and mapa_data.get("last_clicked"):
        clique = mapa_data["last_clicked"]
        if "ultimo_clique" not in st.session_state or st.session_state.ultimo_clique != clique:
            st.session_state.ultimo_clique = clique
            with st.spinner("Consultando trânsito neste ponto..."):
                try:
                    key = os.getenv("TOMTOM_API_KEY")
                    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={clique['lat']},{clique['lng']}&key={key}"
                    resp = requests.get(url, timeout=10)
                    data = resp.json()
                    if "flowSegmentData" in data:
                        flow = data["flowSegmentData"]
                        vel_atual = flow.get("currentSpeed", 0)
                        vel_livre = flow.get("freeFlowSpeed", 1)
                        pct_lento = max(0, round((1 - vel_atual / vel_livre) * 100, 1))
                        if pct_lento < 20:
                            cor, status, emoji = "#4ade80", "Livre", "🟢"
                        elif pct_lento < 45:
                            cor, status, emoji = "#f5c842", "Moderado", "🟡"
                        else:
                            cor, status, emoji = "#ff6b35", "Lento", "🔴"

                        clique_data = {
                            "lat": round(clique["lat"], 4),
                            "lng": round(clique["lng"], 4),
                            "vel_atual": vel_atual,
                            "vel_livre": vel_livre,
                            "pct_lento": pct_lento,
                            "cor": cor,
                            "status": status,
                            "emoji": emoji
                        }
                        st.session_state.clique_resultado = clique_data

                        # Salva clique no banco
                        salvar_clique_mapa(clique_data)
                    else:
                        st.session_state.clique_resultado = None
                except Exception as e:
                    st.session_state.clique_resultado = {"erro": str(e)}

with col_resultado:
    st.markdown("""
    <div style='background:#0e1419;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:24px'>
        <p style='font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#6b7280;margin-bottom:16px'>Legenda</p>
        <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px'>
            <div style='width:12px;height:12px;border-radius:50%;background:#4ade80'></div>
            <span style='font-size:13px'>Livre — abaixo de 20%</span>
        </div>
        <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px'>
            <div style='width:12px;height:12px;border-radius:50%;background:#f5c842'></div>
            <span style='font-size:13px'>Moderado — entre 20% e 45%</span>
        </div>
        <div style='display:flex;align-items:center;gap:10px'>
            <div style='width:12px;height:12px;border-radius:50%;background:#ff6b35'></div>
            <span style='font-size:13px'>Lento — acima de 45%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "clique_resultado" in st.session_state and st.session_state.clique_resultado:
        r = st.session_state.clique_resultado
        if "erro" in r:
            st.error(f"Erro: {r['erro']}")
        else:
            st.markdown(f"""
            <div style='background:#0e1419;border:1px solid {r["cor"]}40;border-radius:14px;padding:24px;margin-top:16px'>
                <p style='font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#6b7280;margin-bottom:8px'>Resultado</p>
                <p style='font-size:12px;color:#6b7280;margin-bottom:16px'>📍 {r["lat"]}, {r["lng"]}</p>
                <div style='font-family:Bebas Neue,sans-serif;font-size:52px;color:{r["cor"]};line-height:1;margin-bottom:4px'>{r["vel_atual"]} <span style='font-size:20px'>km/h</span></div>
                <div style='font-size:16px;margin-bottom:20px'>{r["emoji"]} {r["status"]}</div>
                <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px'>
                    <div style='background:#141c24;border-radius:8px;padding:12px'>
                        <div style='font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#6b7280;margin-bottom:4px'>Vel. livre</div>
                        <div style='font-size:18px;font-weight:500'>{r["vel_livre"]} km/h</div>
                    </div>
                    <div style='background:#141c24;border-radius:8px;padding:12px'>
                        <div style='font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#6b7280;margin-bottom:4px'>Lentidão</div>
                        <div style='font-size:18px;font-weight:500;color:{r["cor"]}'>{r["pct_lento"]}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#0e1419;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:24px;margin-top:16px;text-align:center'>
            <div style='font-size:32px;margin-bottom:12px'>👆</div>
            <p style='color:#6b7280;font-size:14px;line-height:1.6'>Clique em qualquer ponto do mapa para ver o trânsito em tempo real.</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# HISTÓRICO DO BANCO
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("<p style='font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#f5c842'>Histórico</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-family:Bebas Neue,sans-serif;font-size:32px;letter-spacing:1px'>SNAPSHOTS NO BANCO</p>", unsafe_allow_html=True)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM snapshots")
        total = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        st.metric("Total no banco", f"{total} snapshots")
        snapshots = buscar_ultimos_snapshots(limit=5)
        for s in snapshots:
            ts = str(s['timestamp'])[:16]
            score = s.get('score', '—')
            vel = s.get('velocidade_atual', '—')
            clima = str(s.get('clima_desc', '—')).capitalize()
            st.markdown(f"""
            <div class='snap-card' style='color:#e8e4dc'>
                🕐 {ts} &nbsp;|&nbsp; Score: <b>{score}</b> &nbsp;|&nbsp; {vel} km/h &nbsp;|&nbsp; {clima}
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro ao buscar banco: {e}")

with col_b:
    st.markdown("<p style='font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#f5c842'>Último registro</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-family:Bebas Neue,sans-serif;font-size:32px;letter-spacing:1px'>DADOS SALVOS</p>", unsafe_allow_html=True)
    try:
        ultimo = buscar_ultimo_snapshot()
        if ultimo:
            col_x, col_y, col_z = st.columns(3)
            col_x.metric("Score", ultimo.get("score", "—"))
            col_y.metric("Hora", f"{ultimo.get('hour', '—')}h")
            col_z.metric("Velocidade", f"{ultimo.get('velocidade_atual', '—')} km/h")
            st.markdown(f"""
            <div class='snap-card' style='color:#e8e4dc;margin-top:12px'>
                🌤️ {str(ultimo.get('clima_desc', '—')).capitalize()} &nbsp;|&nbsp;
                🌡️ {ultimo.get('temp', '—')}°C &nbsp;|&nbsp;
                💧 {ultimo.get('umidade', '—')}%
            </div>
            """, unsafe_allow_html=True)

        # Histórico de rotas
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#f5c842;margin-bottom:10px'>Últimas rotas calculadas</p>", unsafe_allow_html=True)
        rotas = buscar_historico_rotas(limit=3)
        for rota in rotas:
            st.markdown(f"""
            <div class='snap-card' style='color:#e8e4dc'>
                🚗 {str(rota.get('origem',''))[:30]} → {str(rota.get('destino',''))[:30]}<br>
                <span style='color:#6b7280;font-size:11px'>{rota.get('distancia_km')} km · {rota.get('tempo_min')} min · R$ {rota.get('custo_min'):.0f}–{rota.get('custo_max'):.0f}</span>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro: {e}")

st.divider()
st.markdown("""
<p style='text-align:center;color:#6b7280;font-size:13px'>
    <span style='font-family:Bebas Neue,sans-serif;color:#f5c842;font-size:18px'>VAIAGORA</span>
    &nbsp;·&nbsp; Feito com ☕ e Python em SP &nbsp;·&nbsp; 2026
</p>
""", unsafe_allow_html=True)