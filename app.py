import streamlit as st
import os
import json
import folium
import requests
from streamlit_folium import st_folium
from datetime import datetime
from dotenv import load_dotenv
from src.collector import get_weather_sp, get_traffic_tomtom, calcular_score

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
.resultado-card {
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
    analisar = st.button("🔍 Analisar agora")

if "analise" not in st.session_state:
    st.session_state.analise = None

if analisar:
    with st.spinner("Consultando clima e trânsito de SP..."):
        try:
            weather = get_weather_sp()
            traffic = get_traffic_tomtom()
            score = calcular_score(weather, traffic)
            st.session_state.analise = {
                "weather": weather,
                "traffic": traffic,
                "score": score
            }
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

# MAPA INTERATIVO
st.markdown("<p style='font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#f5c842'>Mapa interativo</p>", unsafe_allow_html=True)
st.markdown("<p style='font-family:Bebas Neue,sans-serif;font-size:32px;letter-spacing:1px'>CLIQUE NO MAPA PARA VER O TRÂNSITO</p>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;font-size:14px;margin-bottom:20px'>Clique em qualquer ponto de São Paulo para consultar o trânsito daquela região em tempo real.</p>", unsafe_allow_html=True)

col_mapa, col_resultado = st.columns([3, 2])

with col_mapa:
    # Mapa base escuro centralizado em SP
    m = folium.Map(
        location=[-23.5505, -46.6333],
        zoom_start=12,
        tiles="CartoDB dark_matter"
    )

    # Marcador do último clique
    if "ultimo_clique" in st.session_state and st.session_state.ultimo_clique:
        lat = st.session_state.ultimo_clique["lat"]
        lon = st.session_state.ultimo_clique["lng"]

        if "clique_resultado" in st.session_state and st.session_state.clique_resultado:
            r = st.session_state.clique_resultado
            cor = r["cor"]
        else:
            cor = "#f5c842"

        folium.CircleMarker(
            location=[lat, lon],
            radius=16,
            color=cor,
            fill=True,
            fill_color=cor,
            fill_opacity=0.8,
            tooltip="📍 Ponto selecionado"
        ).add_to(m)

    # Captura clique no mapa
    mapa_data = st_folium(
        m,
        width=None,
        height=480,
        returned_objects=["last_clicked"]
    )

    # Processa clique
    if mapa_data and mapa_data.get("last_clicked"):
        clique = mapa_data["last_clicked"]
        lat = clique["lat"]
        lng = clique["lng"]

        # Só consulta se for um clique novo
        if "ultimo_clique" not in st.session_state or st.session_state.ultimo_clique != clique:
            st.session_state.ultimo_clique = clique
            with st.spinner("Consultando trânsito neste ponto..."):
                try:
                    key = os.getenv("TOMTOM_API_KEY")
                    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lng}&key={key}"
                    resp = requests.get(url, timeout=10)
                    data = resp.json()

                    if "flowSegmentData" in data:
                        flow = data["flowSegmentData"]
                        vel_atual = flow.get("currentSpeed", 0)
                        vel_livre = flow.get("freeFlowSpeed", 1)
                        pct_lento = max(0, round((1 - vel_atual / vel_livre) * 100, 1))
                        confianca = flow.get("confidence", 0)

                        if pct_lento < 20:
                            cor, status, emoji = "#4ade80", "Livre", "🟢"
                        elif pct_lento < 45:
                            cor, status, emoji = "#f5c842", "Moderado", "🟡"
                        else:
                            cor, status, emoji = "#ff6b35", "Lento", "🔴"

                        st.session_state.clique_resultado = {
                            "lat": round(lat, 4),
                            "lng": round(lng, 4),
                            "vel_atual": vel_atual,
                            "vel_livre": vel_livre,
                            "pct_lento": pct_lento,
                            "confianca": confianca,
                            "cor": cor,
                            "status": status,
                            "emoji": emoji
                        }
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
            <span style='font-size:13px'>Livre — abaixo de 20% lento</span>
        </div>
        <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px'>
            <div style='width:12px;height:12px;border-radius:50%;background:#f5c842'></div>
            <span style='font-size:13px'>Moderado — entre 20% e 45%</span>
        </div>
        <div style='display:flex;align-items:center;gap:10px;margin-bottom:0'>
            <div style='width:12px;height:12px;border-radius:50%;background:#ff6b35'></div>
            <span style='font-size:13px'>Lento — acima de 45%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Resultado do clique
    if "clique_resultado" in st.session_state and st.session_state.clique_resultado:
        r = st.session_state.clique_resultado

        if "erro" in r:
            st.error(f"Erro: {r['erro']}")
        else:
            st.markdown(f"""
            <div style='background:#0e1419;border:1px solid {r["cor"]}40;border-radius:14px;padding:24px;margin-top:16px'>
                <p style='font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#6b7280;margin-bottom:8px'>Resultado do clique</p>
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
            <p style='color:#6b7280;font-size:14px;line-height:1.6'>Clique em qualquer ponto do mapa para ver o trânsito em tempo real naquela região.</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# HISTÓRICO
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("<p style='font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#f5c842'>Histórico</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-family:Bebas Neue,sans-serif;font-size:32px;letter-spacing:1px'>SNAPSHOTS COLETADOS</p>", unsafe_allow_html=True)
    raw_path = "data/raw"
    if os.path.exists(raw_path):
        files = sorted(os.listdir(raw_path), reverse=True)
        st.metric("Total", f"{len(files)} snapshots")
        for f in files[:5]:
            st.markdown(f"<div class='snap-card'>{f}</div>", unsafe_allow_html=True)

with col_b:
    st.markdown("<p style='font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#f5c842'>Último registro</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-family:Bebas Neue,sans-serif;font-size:32px;letter-spacing:1px'>DADOS SALVOS</p>", unsafe_allow_html=True)
    if os.path.exists("data/raw"):
        files = sorted(os.listdir("data/raw"), reverse=True)
        if files:
            with open(f"data/raw/{files[0]}") as f:
                ultimo = json.load(f)
            col_x, col_y, col_z = st.columns(3)
            col_x.metric("Score", ultimo.get("score", "—"))
            col_y.metric("Hora", f"{ultimo.get('hour', '—')}h")
            col_z.metric("Velocidade", f"{ultimo.get('traffic', {}).get('velocidade_atual_kmh', '—')} km/h")

st.divider()
st.markdown("""
<p style='text-align:center;color:#6b7280;font-size:13px'>
    <span style='font-family:Bebas Neue,sans-serif;color:#f5c842;font-size:18px'>VAIAGORA</span>
    &nbsp;·&nbsp; Feito com ☕ e Python em SP &nbsp;·&nbsp; 2026
</p>
""", unsafe_allow_html=True)