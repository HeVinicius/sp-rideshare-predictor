import os
import json
from datetime import datetime
from src.database import salvar_snapshot

pasta = "data/raw"
arquivos = sorted(os.listdir(pasta))
total = len(arquivos)
migrados = 0
erros = 0

print(f"🔄 Encontrados {total} arquivos JSON para migrar...\n")

for arquivo in arquivos:
    if not arquivo.endswith(".json"):
        continue
    caminho = os.path.join(pasta, arquivo)
    try:
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        salvar_snapshot(data)
        migrados += 1
        print(f"✓ {arquivo}")
    except Exception as e:
        erros += 1
        print(f"✗ {arquivo} — Erro: {e}")

print(f"\n✅ Migração concluída!")
print(f"   Migrados: {migrados}")
print(f"   Erros: {erros}")