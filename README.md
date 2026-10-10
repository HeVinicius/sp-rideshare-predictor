# VaiAgora SP

Projeto em Python que analisa dados de clima, eventos e trânsito em São Paulo para ajudar a identificar bons horários para solicitar corridas de Uber e 99 baseado em análise preditiva.

## Funcionalidades

- Indicador de condições para solicitar uma corrida, com pontuação de 0 a 100.
- Consulta de clima em tempo real.
- Consulta de trânsito pela API da TomTom.
- Mapa interativo com pontos de São Paulo.
- Coleta periódica de dados para análise histórica.

## Tecnologias

- Python 3.11
- Streamlit
- Pandas e Scikit-learn
- Folium e streamlit-folium
- TomTom Traffic API
- OpenWeatherMap API
- XGBoost e LightGBM

## Como executar

Clone o repositório:

```bash
git clone https://github.com/HeVinicius/sp-rideshare-predictor.git
cd sp-rideshare-predictor
```

Crie e ative o ambiente virtual:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux ou macOS:

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Configure as chaves de API no arquivo `.env`, utilizando `.env.example` como referência. As chaves podem ser obtidas nos sites da [OpenWeatherMap](https://openweathermap.org/) e da [TomTom](https://developer.tomtom.com/).

Inicie a coleta de dados e o dashboard em terminais separados:

```bash
python scheduler.py
```

```bash
streamlit run app.py
```

Acesse o dashboard em http://localhost:8501.

## Estrutura do projeto

```text
sp-rideshare-predictor/
├── src/
│   ├── collector.py
│   └── features.py
├── data/
│   └── raw/
├── models/
├── app.py
├── scheduler.py
├── .env.example
└── requirements.txt
```

## Regiões monitoradas

Centro, Paulista, Faria Lima, Pinheiros, Vila Olímpia, Berrini, Mooca, Tatuapé, Santana, Marginal Tietê, Marginal Pinheiros, Guarulhos e Santo André.

## Próximas etapas

- Desenvolver o modelo de previsão com dados históricos.
- Estimar as condições de trânsito para as próximas horas.
- Implementar notificações.
- Desenvolver uma versão mobile.