import schedule
import time
from src.collector import collect_snapshot

print("Script iniciado! Coletando dados de SP a cada 05 minutos...")
print("Deixe essa janela aberta. Pressione Ctrl+C para parar.\n")

# Coleta imediatamente ao iniciar
collect_snapshot()

# coleta a cada 5 minutos
schedule.every(5).minutes.do(collect_snapshot)

while True:
    schedule.run_pending()
    time.sleep(60)