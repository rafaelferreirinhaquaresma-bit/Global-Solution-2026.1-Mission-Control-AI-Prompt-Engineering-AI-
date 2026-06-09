"""
src/engine.py — Motor de análise da Mission Control AI (Trilha AgroSat).

Este arquivo contém:
  - Função llm(): único ponto de integração com o modelo de linguagem.
  - Classe MissionEngine: orquestra telemetria, alertas e chamadas à IA.
"""

import os
from ollama import Client
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

from src.telemetria import coletar, resumo_textual
from src.alertas import avaliar, nivel_geral, resumo_alertas

load_dotenv()

# Identificação da trilha
TRILHA = "agrosat"

# ──────────────────────────────────────────────────────────
# Configuração do cliente Ollama Cloud
# ──────────────────────────────────────────────────────────
_api_key = os.environ.get("OLLAMA_API_KEY", "")
client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + _api_key}
)

print("API KEY carregada:", "OK ✅" if _api_key else "FALTANDO ❌")


# ──────────────────────────────────────────────────────────
# Função llm() — ponto único de contato com o modelo
# ──────────────────────────────────────────────────────────

def llm(prompt: str, system: str = None, max_tokens: int = 800, temperature: float = 0.3) -> str:
    """
    Envia prompt ao gpt-oss:120b via Ollama Cloud e retorna o texto da resposta.

    Args:
        prompt      : Mensagem do usuário / prompt dinâmico com dados da missão.
        system      : System prompt (carregado do arquivo prompts/system_prompt.md).
        max_tokens  : Limite de tokens na resposta.
        temperature : Criatividade do modelo (0.3 = respostas consistentes).

    Returns:
        Texto da resposta do modelo, ou mensagem de erro.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        resposta = client.chat(
            model="gpt-oss:120b",
            messages=messages,
            options={"num_predict": max_tokens, "temperature": temperature},
            stream=False
        )
        return resposta["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Erro ao consultar IA: {e}"


# ──────────────────────────────────────────────────────────
# Carrega o system prompt do arquivo markdown
# ──────────────────────────────────────────────────────────

def load_system_prompt() -> str:
    """Lê o system prompt do arquivo prompts/system_prompt.md."""
    path = Path("prompts/system_prompt.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Fallback mínimo caso o arquivo não exista
    return (
        "Você é o sistema de inteligência artificial Mission Control AI, "
        "especializado em monitoramento do satélite AgroSat-1. "
        "Analise os dados de telemetria e explique o impacto terrestre no agronegócio brasileiro."
    )


# ──────────────────────────────────────────────────────────
# Classe MissionEngine
# ──────────────────────────────────────────────────────────

class MissionEngine:
    """
    Motor central do Mission Control AI.

    Responsabilidades:
      1. Coletar dados de telemetria (src/telemetria.py)
      2. Avaliar alertas via regras Python (src/alertas.py)
      3. Construir prompt contextualizado com dados reais
      4. Chamar o LLM para análise em linguagem natural
      5. Retornar resposta formatada para a CLI
    """

    def __init__(self):
        self.trilha = TRILHA
        self.system_prompt = load_system_prompt()
        self._historico: list = []          # Memória dos últimos ciclos
        self._max_historico: int = 3        # Quantos ciclos manter no contexto
        self._ultimo_dados: dict = {}
        self._ultimo_nivel: str = "N/A"
        self._ciclos_analisados: int = 0

    def is_ready(self) -> bool:
        """Retorna True — engine completamente implementado."""
        return True

    # ── Snapshot de status ────────────────────────────────

    def status_snapshot(self) -> str:
        """Retorna texto resumindo o estado atual da telemetria sem acionar a IA."""
        dados = coletar()
        alertas = avaliar(dados)
        nivel = nivel_geral(alertas)

        self._ultimo_dados = dados
        self._ultimo_nivel = nivel

        linhas = [
            f"🛰  [AgroSat-1] Status em {dados['timestamp']}",
            f"📊  Nível geral da missão: {self._badge_nivel(nivel)}",
            "",
            resumo_textual(dados),
            "",
            "─── Alertas ─────────────────────────────────────",
            resumo_alertas(alertas),
        ]
        return "\n".join(linhas)

    # ── Análise principal (com IA) ────────────────────────

    def analyze(self, pergunta_usuario: str) -> str:
        """
        Analisa a pergunta com base na telemetria atual + alertas + IA generativa.

        Fluxo:
          1. Coleta telemetria simulada
          2. Avalia alertas em Python
          3. Monta prompt dinâmico com dados reais injetados
          4. Chama LLM com system prompt contextual
          5. Armazena no histórico (memória de contexto)
          6. Retorna resposta formatada
        """
        # 1. Coleta de dados
        dados = coletar()
        alertas = avaliar(dados)
        nivel = nivel_geral(alertas)

        # Atualiza estado interno
        self._ultimo_dados = dados
        self._ultimo_nivel = nivel
        self._ciclos_analisados += 1

        # 2. Registra no histórico (memória de contexto)
        self._historico.append({
            "ciclo": dados["ciclo"],
            "timestamp": dados["timestamp"],
            "nivel": nivel,
            "ndvi": dados["ndvi_sensor_saude"],
            "temperatura": dados["temperatura_payload"],
            "armazenamento": dados["armazenamento"],
        })
        # Mantém apenas os últimos N ciclos
        if len(self._historico) > self._max_historico:
            self._historico.pop(0)

        # 3. Monta o prompt dinâmico com dados reais injetados
        prompt = self._montar_prompt(pergunta_usuario, dados, alertas, nivel)

        # 4. Chama o LLM
        resposta = llm(prompt, system=self.system_prompt, max_tokens=800, temperature=0.3)

        return resposta

    # ── Montagem do prompt dinâmico ───────────────────────

    def _montar_prompt(self, pergunta: str, dados: dict, alertas: list, nivel: str) -> str:
        """
        Constrói o prompt com os dados da telemetria injetados dinamicamente.

        Técnicas aplicadas:
          - Injeção de dados reais (não hardcoded)
          - Memória de contexto dos últimos ciclos
          - Exemplos de formato de resposta esperado (few-shot)
          - Indicação explícita do nível de criticidade
        """
        historico_texto = self._formatar_historico()

        prompt = f"""
## DADOS DE TELEMETRIA — CICLO {dados['ciclo']} — {dados['timestamp']}

**Satélite:** {dados['satelite']} | **Órbita:** {dados['orbita']}
**Nível geral da missão:** {nivel}

### Leituras dos sensores:
- Saúde do Sensor NDVI: {dados['ndvi_sensor_saude']}%
- Temperatura do Payload: {dados['temperatura_payload']}°C
- Armazenamento Disponível: {dados['armazenamento']}%
- Janela de Downlink: {dados['janela_downlink']} min
- Desvio de Atitude: {dados['estabilidade_atitude']}°

### Alertas detectados (lógica Python):
{resumo_alertas(alertas)}

{historico_texto}

---

## PERGUNTA DO OPERADOR:
{pergunta}

---

## INSTRUÇÕES DE RESPOSTA:
1. Analise os dados acima com foco nos parâmetros em alerta.
2. Explique o que cada anomalia significa TECNICAMENTE para o satélite.
3. Traduza o impacto para o AGRONEGÓCIO BRASILEIRO (produtor rural, analista de seguro, cooperativa).
4. Se houver parâmetros CRÍTICOS, inicie a resposta com 🚨 e indique ação prioritária.
5. Seja objetivo: máximo 4 parágrafos. Use linguagem técnica mas acessível a operadores não-especialistas.
"""
        return prompt.strip()

    def _formatar_historico(self) -> str:
        """Formata o histórico dos últimos ciclos para injeção no prompt."""
        if not self._historico:
            return ""
        linhas = ["### Histórico dos últimos ciclos (memória de contexto):"]
        for h in self._historico:
            linhas.append(
                f"- Ciclo {h['ciclo']} ({h['timestamp']}): Nível={h['nivel']} | "
                f"NDVI={h['ndvi']}% | Temp={h['temperatura']}°C | "
                f"Armazenamento={h['armazenamento']}%"
            )
        return "\n".join(linhas)

    @staticmethod
    def _badge_nivel(nivel: str) -> str:
        badges = {
            "NORMAL": "🟢 NORMAL",
            "ATENÇÃO": "🟡 ATENÇÃO",
            "CRÍTICO": "🔴 CRÍTICO",
        }
        return badges.get(nivel, nivel)
