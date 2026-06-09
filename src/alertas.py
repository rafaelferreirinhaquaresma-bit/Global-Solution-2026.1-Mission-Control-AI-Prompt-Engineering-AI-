"""
src/alertas.py — Thresholds e lógica de alertas do AgroSat.

Toda lógica de decisão fica AQUI, em código Python puro.
A IA contextualiza e explica — mas quem decide se é crítico é este módulo.

Níveis de alerta:
  NORMAL   — parâmetro dentro da faixa esperada
  ATENÇÃO  — parâmetro fora do nominal mas ainda operacional
  CRÍTICO  — parâmetro em nível de falha que exige ação imediata
"""

from dataclasses import dataclass, field
from typing import List


# ──────────────────────────────────────────────────────────
# Estrutura de um alerta individual
# ──────────────────────────────────────────────────────────
@dataclass
class Alerta:
    parametro: str
    nivel: str          # "NORMAL" | "ATENÇÃO" | "CRÍTICO"
    valor: float
    mensagem: str
    acao_automatica: str = ""
    impacto_terrestre: str = ""


# ──────────────────────────────────────────────────────────
# Thresholds de cada parâmetro (lógica em Python, não no prompt)
# ──────────────────────────────────────────────────────────

def _avaliar_ndvi(valor: float) -> Alerta:
    if valor >= 85.0:
        return Alerta(
            parametro="ndvi_sensor_saude",
            nivel="NORMAL",
            valor=valor,
            mensagem=f"Sensor NDVI operando normalmente ({valor}%).",
            impacto_terrestre="Imagens multiespectrais disponíveis para análise de safras."
        )
    elif valor >= 65.0:
        return Alerta(
            parametro="ndvi_sensor_saude",
            nivel="ATENÇÃO",
            valor=valor,
            mensagem=f"Degradação parcial do sensor NDVI detectada ({valor}%). Monitorar.",
            acao_automatica="Ativando modo de calibração automática do sensor.",
            impacto_terrestre=(
                "Redução na precisão dos índices de vegetação. "
                "Analistas de seguro agrícola podem receber dados imprecisos."
            )
        )
    else:
        return Alerta(
            parametro="ndvi_sensor_saude",
            nivel="CRÍTICO",
            valor=valor,
            mensagem=f"FALHA CRÍTICA no sensor NDVI ({valor}%). Imagens comprometidas!",
            acao_automatica="Suspendendo captura de imagens. Notificando equipe de solo.",
            impacto_terrestre=(
                "IMPACTO SEVERO: produtores rurais ficam sem dados de índice de vegetação. "
                "Monitoramento de safras, irrigação inteligente e seguro rural baseado em índice "
                "ficam indisponíveis até restauração do sensor."
            )
        )


def _avaliar_temperatura(valor: float) -> Alerta:
    if -10.0 <= valor <= 55.0:
        return Alerta(
            parametro="temperatura_payload",
            nivel="NORMAL",
            valor=valor,
            mensagem=f"Temperatura do payload nominal ({valor}°C).",
            impacto_terrestre="Sistema óptico operando dentro dos parâmetros de projeto."
        )
    elif valor > 55.0 and valor <= 70.0:
        return Alerta(
            parametro="temperatura_payload",
            nivel="ATENÇÃO",
            valor=valor,
            mensagem=f"Temperatura elevada no payload óptico ({valor}°C). Limite: 55°C.",
            acao_automatica="Ativando dissipador térmico auxiliar e reduzindo duty cycle do sensor.",
            impacto_terrestre=(
                "Qualidade das imagens pode ser reduzida por expansão térmica das lentes. "
                "Recomendado aguardar saída do eclipse antes de captura crítica."
            )
        )
    elif valor > 70.0:
        return Alerta(
            parametro="temperatura_payload",
            nivel="CRÍTICO",
            valor=valor,
            mensagem=f"TEMPERATURA CRÍTICA no payload ({valor}°C)! Risco de dano permanente.",
            acao_automatica="Desligando sensor óptico. Entrando em modo de segurança térmico.",
            impacto_terrestre=(
                "RISCO DE PERDA TOTAL do payload óptico. "
                "Interrupção completa do serviço de sensoriamento para o agronegócio."
            )
        )
    elif valor < -10.0:
        return Alerta(
            parametro="temperatura_payload",
            nivel="ATENÇÃO",
            valor=valor,
            mensagem=f"Temperatura abaixo do limite inferior ({valor}°C). Verificar aquecedor.",
            acao_automatica="Ativando resistências de aquecimento do payload.",
            impacto_terrestre="Sensor pode não operar até atingir temperatura mínima operacional."
        )
    return Alerta(parametro="temperatura_payload", nivel="NORMAL", valor=valor,
                  mensagem=f"Temperatura nominal ({valor}°C).")


def _avaliar_armazenamento(valor: float) -> Alerta:
    if valor >= 20.0:
        return Alerta(
            parametro="armazenamento",
            nivel="NORMAL",
            valor=valor,
            mensagem=f"Armazenamento com espaço adequado ({valor}%).",
            impacto_terrestre="Capacidade suficiente para registrar múltiplas passagens sobre áreas agrícolas."
        )
    elif valor >= 10.0:
        return Alerta(
            parametro="armazenamento",
            nivel="ATENÇÃO",
            valor=valor,
            mensagem=f"Armazenamento abaixo de 20% ({valor}%). Priorizar downlink.",
            acao_automatica="Compressão de imagens ativada. Aguardando próxima janela de downlink.",
            impacto_terrestre=(
                "Risco de perda de imagens se janela de downlink for adiada. "
                "Produtores aguardando dados de campo podem sofrer atraso na tomada de decisão."
            )
        )
    else:
        return Alerta(
            parametro="armazenamento",
            nivel="CRÍTICO",
            valor=valor,
            mensagem=f"ARMAZENAMENTO CRÍTICO ({valor}%)! Novas imagens serão descartadas!",
            acao_automatica=(
                "PAUSANDO captura de novas imagens. "
                "Iniciando transmissão emergencial de dados prioritários."
            ),
            impacto_terrestre=(
                "PERDA DE DADOS IMINENTE. Imagens de lavouras em monitoramento contínuo "
                "serão descartadas. Analistas de seguro agrícola e cooperativas afetados diretamente."
            )
        )


def _avaliar_downlink(valor: float) -> Alerta:
    if valor >= 10.0:
        return Alerta(
            parametro="janela_downlink",
            nivel="NORMAL",
            valor=valor,
            mensagem=f"Janela de downlink adequada ({valor} min).",
            impacto_terrestre="Transmissão de imagens para estação terrestre garantida nesta passagem."
        )
    elif valor >= 5.0:
        return Alerta(
            parametro="janela_downlink",
            nivel="ATENÇÃO",
            valor=valor,
            mensagem=f"Janela de downlink curta ({valor} min). Priorizar dados críticos.",
            acao_automatica="Selecionando apenas imagens prioritárias para transmissão.",
            impacto_terrestre=(
                "Apenas parte dos dados capturados será transmitida nesta passagem. "
                "Dados de regiões com alerta de seca ou pragas serão priorizados."
            )
        )
    else:
        return Alerta(
            parametro="janela_downlink",
            nivel="CRÍTICO",
            valor=valor,
            mensagem=f"JANELA DE DOWNLINK INSUFICIENTE ({valor} min)! Transmissão comprometida.",
            acao_automatica=(
                "Abortando downlink completo. "
                "Armazenando para próxima janela. Acionando estação terrestre de backup."
            ),
            impacto_terrestre=(
                "Dados da missão retidos no satélite. Produtores rurais e plataformas como "
                "Climate FieldView e Embrapa Monitora não receberão atualização neste ciclo."
            )
        )


def _avaliar_atitude(valor: float) -> Alerta:
    if valor <= 0.03:
        return Alerta(
            parametro="estabilidade_atitude",
            nivel="NORMAL",
            valor=valor,
            mensagem=f"Estabilidade de atitude excelente (desvio: {valor}°).",
            impacto_terrestre="Apontamento preciso garante imagens de alta resolução espacial."
        )
    elif valor <= 0.05:
        return Alerta(
            parametro="estabilidade_atitude",
            nivel="ATENÇÃO",
            valor=valor,
            mensagem=f"Desvio de atitude no limite superior ({valor}°). Verificar rodas de reação.",
            acao_automatica="Iniciando correção de atitude por rodas de reação.",
            impacto_terrestre=(
                "Leve degradação na resolução espacial das imagens. "
                "Análises de precisão de campo podem ser comprometidas."
            )
        )
    else:
        return Alerta(
            parametro="estabilidade_atitude",
            nivel="CRÍTICO",
            valor=valor,
            mensagem=f"INSTABILIDADE DE ATITUDE ({valor}°)! Imagens inutilizáveis!",
            acao_automatica=(
                "Suspendendo captura. Ativando thruster de correção de atitude. "
                "Aguardando estabilização antes de retomar operação."
            ),
            impacto_terrestre=(
                "TODAS as imagens capturadas no período estão borradas e inutilizáveis. "
                "Regiões agrícolas monitoradas ficam sem cobertura. "
                "Agricultura de precisão e seguros baseados em índice totalmente impactados."
            )
        )


# ──────────────────────────────────────────────────────────
# Função principal — avalia todos os parâmetros
# ──────────────────────────────────────────────────────────

def avaliar(dados: dict) -> List[Alerta]:
    """
    Avalia todos os parâmetros de telemetria e retorna lista de alertas.

    Args:
        dados: Dicionário retornado por telemetria.coletar()

    Returns:
        Lista de Alerta, um por parâmetro monitorado.
    """
    alertas = [
        _avaliar_ndvi(dados["ndvi_sensor_saude"]),
        _avaliar_temperatura(dados["temperatura_payload"]),
        _avaliar_armazenamento(dados["armazenamento"]),
        _avaliar_downlink(dados["janela_downlink"]),
        _avaliar_atitude(dados["estabilidade_atitude"]),
    ]
    return alertas


def nivel_geral(alertas: List[Alerta]) -> str:
    """Retorna o nível geral da missão com base nos alertas."""
    niveis = [a.nivel for a in alertas]
    if "CRÍTICO" in niveis:
        return "CRÍTICO"
    elif "ATENÇÃO" in niveis:
        return "ATENÇÃO"
    return "NORMAL"


def resumo_alertas(alertas: List[Alerta]) -> str:
    """Formata a lista de alertas em texto legível para o prompt."""
    icones = {"NORMAL": "✅", "ATENÇÃO": "⚠️", "CRÍTICO": "🚨"}
    linhas = []
    for a in alertas:
        icone = icones.get(a.nivel, "❓")
        linhas.append(f"{icone} [{a.nivel}] {a.mensagem}")
        if a.acao_automatica:
            linhas.append(f"   → Ação automática: {a.acao_automatica}")
        if a.impacto_terrestre:
            linhas.append(f"   🌍 Impacto terrestre: {a.impacto_terrestre}")
    return "\n".join(linhas)
