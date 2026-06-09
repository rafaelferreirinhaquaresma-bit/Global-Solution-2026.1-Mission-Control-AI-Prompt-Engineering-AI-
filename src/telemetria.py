"""
src/telemetria.py — Simulação de telemetria do satélite AgroSat.

Parâmetros monitorados (Trilha AgroSat):
  - ndvi_sensor_saude   : Saúde do sensor multiespectral (índice NDVI) — %
  - temperatura_payload : Temperatura do payload óptico — °C
  - armazenamento       : Capacidade de armazenamento disponível — %
  - janela_downlink     : Minutos disponíveis na janela de downlink — min
  - estabilidade_atitude: Desvio de atitude do satélite — graus (< 0.05 = OK)
"""

import random
from datetime import datetime


# ──────────────────────────────────────────────────────────
# Faixas nominais de operação (referência para alertas)
# ──────────────────────────────────────────────────────────
FAIXAS_NOMINAIS = {
    "ndvi_sensor_saude": (85.0, 100.0),      # % — abaixo de 85% é alerta
    "temperatura_payload": (-10.0, 55.0),    # °C — fora dessa faixa é alerta
    "armazenamento": (10.0, 100.0),          # % — abaixo de 10% é crítico
    "janela_downlink": (5.0, 60.0),          # min — abaixo de 5 min é crítico
    "estabilidade_atitude": (0.0, 0.05),     # graus — acima de 0.05 é alerta
}

# Descrições legíveis para cada parâmetro
DESCRICOES = {
    "ndvi_sensor_saude": "Saúde do Sensor NDVI (%)",
    "temperatura_payload": "Temperatura do Payload (°C)",
    "armazenamento": "Armazenamento Disponível (%)",
    "janela_downlink": "Janela de Downlink (min)",
    "estabilidade_atitude": "Desvio de Atitude (°)",
}

# Unidades de cada parâmetro
UNIDADES = {
    "ndvi_sensor_saude": "%",
    "temperatura_payload": "°C",
    "armazenamento": "%",
    "janela_downlink": "min",
    "estabilidade_atitude": "°",
}

# Controle de ciclo para simular degradação gradual
_ciclo = 0


def coletar(forcar_critico: bool = False) -> dict:
    """
    Gera leitura simulada de todos os parâmetros do AgroSat.

    Args:
        forcar_critico: Se True, simula cenário de falha crítica (para testes).

    Returns:
        Dicionário com os dados da telemetria + metadados de timestamp e ciclo.
    """
    global _ciclo
    _ciclo += 1

    if forcar_critico:
        dados = _cenario_critico()
    else:
        dados = _leitura_normal()

    dados["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dados["ciclo"] = _ciclo
    dados["satelite"] = "AgroSat-1"
    dados["orbita"] = "LEO 650km"

    return dados


def _leitura_normal() -> dict:
    """Leitura com variações plausíveis em torno dos valores nominais."""
    return {
        # Sensor NDVI levemente degradado em operação contínua
        "ndvi_sensor_saude": round(random.uniform(78.0, 99.5), 2),

        # Temperatura varia conforme entrada/saída de eclipse orbital
        "temperatura_payload": round(random.uniform(-5.0, 62.0), 2),

        # Armazenamento consome conforme imagens capturadas
        "armazenamento": round(random.uniform(8.0, 95.0), 2),

        # Janela de downlink varia conforme posição da estação terrestre
        "janela_downlink": round(random.uniform(2.0, 45.0), 2),

        # Microvibrações do satélite
        "estabilidade_atitude": round(random.uniform(0.001, 0.08), 4),
    }


def _cenario_critico() -> dict:
    """Simula falha grave em múltiplos parâmetros simultaneamente."""
    return {
        "ndvi_sensor_saude": round(random.uniform(30.0, 60.0), 2),
        "temperatura_payload": round(random.uniform(70.0, 95.0), 2),
        "armazenamento": round(random.uniform(1.0, 8.0), 2),
        "janela_downlink": round(random.uniform(0.5, 3.0), 2),
        "estabilidade_atitude": round(random.uniform(0.1, 0.3), 4),
    }


def resumo_textual(dados: dict) -> str:
    """Formata os dados de telemetria em texto legível para humanos e para o prompt."""
    linhas = [
        f"🛰  Satélite  : {dados.get('satelite', 'AgroSat-1')} | Órbita: {dados.get('orbita', 'LEO')}",
        f"🕐  Timestamp : {dados.get('timestamp', 'N/A')} | Ciclo: {dados.get('ciclo', '?')}",
        "─" * 50,
        f"📡  NDVI Sensor Saúde      : {dados['ndvi_sensor_saude']} %",
        f"🌡  Temp. Payload          : {dados['temperatura_payload']} °C",
        f"💾  Armazenamento Disp.    : {dados['armazenamento']} %",
        f"📶  Janela de Downlink     : {dados['janela_downlink']} min",
        f"🎯  Desvio de Atitude      : {dados['estabilidade_atitude']} °",
    ]
    return "\n".join(linhas)
