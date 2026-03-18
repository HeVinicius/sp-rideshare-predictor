# 🚗 VaiAgora SP

> Previsão inteligente do melhor horário para chamar Uber ou 99 em São Paulo.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![TomTom](https://img.shields.io/badge/TomTom-API-black)

## 📌 Sobre o projeto

O **VaiAgora SP** é um software que analisa dados em tempo real de clima, trânsito e padrões históricos de São Paulo para indicar o melhor momento para chamar um carro de aplicativo — menos espera, menos surge pricing.

## ✨ Funcionalidades

- 🔢 **Score 0–100** em tempo real indicando se é bom momento para chamar
- 🌤️ **Clima ao vivo** via OpenWeatherMap
- 🚦 **Trânsito em tempo real** via TomTom API
- 🗺️ **Mapa interativo** — clique em qualquer ponto de SP para ver o trânsito
- ⏰ **Coleta automática** a cada 30 minutos
- 📊 **Histórico de snapshots** para treinar o modelo de ML

## 🛠️ Tecnologias

- Python 3.11
- Streamlit
- Folium + streamlit-folium
- TomTom Traffic API
- OpenWeatherMap API
- XGBoost / LightGBM
- Pandas / Scikit-learn

## 🚀 Como rodar

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/sp-rideshare-predictor.git
cd sp-rideshare-predictor
```

### 2. Crie o ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as chaves de API
```bash
cp .env.example .env
```
Preencha o `.env` com suas chaves:
- **OpenWeatherMap**: openweathermap.org
- **TomTom**: developer.tomtom.com

### 5. Rode o projeto
Terminal 1 — coleta automática:
```bash
python scheduler.py
```
Terminal 2 — dashboard:
```bash
streamlit run app.py
```

Acesse em: **http://localhost:8501**

## 📁 Estrutura
```
sp-rideshare-predictor/
├── src/
│   ├── collector.py      # Coleta clima e trânsito
│   └── features.py       # Engenharia de features
├── data/
│   └── raw/              # Snapshots coletados
├── models/               # Modelos ML salvos
├── app.py                # Dashboard Streamlit
├── scheduler.py          # Coleta automática
├── .env.example          # Modelo de configuração
└── requirements.txt
```

## 📍 Regiões monitoradas em SP

Centro, Paulista, Faria Lima, Pinheiros, Vila Olímpia, Berrini, Mooca, Tatuapé, Santana, Marginal Tietê, Marginal Pinheiros, Guarulhos, Santo André.

## 🗺️ Roadmap

- [x] Coleta de clima em tempo real
- [x] Integração TomTom Traffic API
- [x] Score 0–100
- [x] Dashboard visual
- [x] Mapa interativo
- [ ] Modelo ML com histórico de 7 dias
- [ ] Previsão das próximas horas
- [ ] Notificações push
- [ ] App mobile
