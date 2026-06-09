"""
src/ui.py — Interface CLI estilo Claude Code para Mission Control AI.

Usa Rich (painéis, tabelas, cores) + prompt-toolkit (input editável com histórico).
Comandos suportados: /help, /status, /cenario, /about, /clear, /exit
"""

import pyfiglet
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich import box
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.history import InMemoryHistory

console = Console()

# Estilo do prompt de input
_prompt_style = Style.from_dict({
    "prompt": "#06B6D4 bold",
})

session = PromptSession(
    style=_prompt_style,
    history=InMemoryHistory(),
)

# Paleta de cores AgroSat
COR_PRIMARIA = "#06B6D4"     # Ciano — cor principal
COR_ACENTO   = "#22C55E"     # Verde — agro/saúde
COR_ALERTA   = "#F59E0B"     # Âmbar — atenção
COR_CRITICO  = "#EF4444"     # Vermelho — crítico
COR_ROXO     = "#A855F7"     # Roxo — brand FIAP
COR_MUTED    = "#8484A0"     # Cinza — textos secundários


# ──────────────────────────────────────────────────────────
# Banner e tela inicial
# ──────────────────────────────────────────────────────────

def show_banner():
    """Exibe o banner ASCII + card de boas-vindas."""
    console.clear()

    # Linha 1 — Global Solution
    try:
        linha1 = pyfiglet.figlet_format("Global Solution", font="ansi_shadow")
        linha2 = pyfiglet.figlet_format("Mission Control", font="ansi_shadow")
    except Exception:
        linha1 = "=== Global Solution ===\n"
        linha2 = "=== Mission Control ===\n"

    console.print()
    console.print(Align.center(Text(linha1, style=f"bold {COR_ROXO}")))
    console.print(Align.center(Text(linha2, style=f"bold {COR_PRIMARIA}")))
    console.print(Align.center(
        Text("── 2026.1 · Prompt Engineering and AI · FIAP ──", style=f"italic {COR_MUTED}")
    ))
    console.print(Align.center(
        Text("🌾  Trilha AgroSat — Sensoriamento Agrícola Orbital", style=f"bold {COR_ACENTO}")
    ))
    console.print()

    # Card de comandos
    tabela = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    tabela.add_column(style=f"bold {COR_PRIMARIA}", width=14)
    tabela.add_column(style=f"{COR_MUTED}")
    tabela.add_row("/status",  "Exibe telemetria atual sem acionar a IA")
    tabela.add_row("/cenario", "Simula cenário de falha crítica e analisa com IA")
    tabela.add_row("/about",   "Informações sobre o projeto e integrantes")
    tabela.add_row("/clear",   "Limpa o terminal e reexibe o banner")
    tabela.add_row("/help",    "Exibe esta lista de comandos")
    tabela.add_row("/exit",    "Encerra o sistema")

    console.print(Panel(
        tabela,
        title=f"[bold {COR_PRIMARIA}]◆ MISSION CONTROL AI[/]",
        subtitle=f"[{COR_MUTED}]AgroSat-1 · gpt-oss:120b via Ollama Cloud[/]",
        border_style=COR_PRIMARIA,
        padding=(0, 1),
    ))
    console.print()


# ──────────────────────────────────────────────────────────
# Renderização de respostas
# ──────────────────────────────────────────────────────────

def show_response(texto: str, titulo: str = "◆ Mission Control AI", nivel: str = "NORMAL"):
    """Renderiza resposta da IA em painel colorido com timestamp."""
    agora = datetime.now().strftime("%H:%M:%S")

    cor_borda = {
        "NORMAL":  COR_ACENTO,
        "ATENÇÃO": COR_ALERTA,
        "CRÍTICO": COR_CRITICO,
    }.get(nivel, COR_PRIMARIA)

    console.print(Panel(
        texto,
        title=f"[bold {cor_borda}]{titulo}[/]",
        subtitle=f"[{COR_MUTED}]{agora}[/]",
        border_style=cor_borda,
        padding=(1, 2),
    ))
    console.print()


def show_info(mensagem: str, estilo: str = "yellow"):
    """Exibe mensagem informativa simples."""
    console.print(f"  [{estilo}]{mensagem}[/]\n")


# ──────────────────────────────────────────────────────────
# Telas de comandos especiais
# ──────────────────────────────────────────────────────────

def show_help():
    """Exibe tabela completa de ajuda."""
    tabela = Table(
        title="Comandos disponíveis",
        box=box.ROUNDED,
        title_style=f"bold {COR_PRIMARIA}",
        border_style=COR_MUTED,
    )
    tabela.add_column("Comando", style=f"bold {COR_PRIMARIA}", width=14)
    tabela.add_column("Descrição", style="white")
    tabela.add_column("Exemplo de uso", style=f"italic {COR_MUTED}")

    tabela.add_row("/status",  "Telemetria atual sem IA", "/status")
    tabela.add_row("/cenario", "Simula falha crítica + análise IA", "/cenario")
    tabela.add_row("/about",   "Informações do projeto", "/about")
    tabela.add_row("/clear",   "Limpar tela", "/clear")
    tabela.add_row("/help",    "Esta ajuda", "/help")
    tabela.add_row("/exit",    "Encerrar sistema", "/exit")
    tabela.add_row(
        "[qualquer texto]",
        "Pergunta livre analisada pela IA com dados da missão",
        "Como está o sensor NDVI?"
    )

    console.print(tabela)
    console.print()


def show_about():
    """Exibe informações do projeto."""
    texto = (
        "[bold]Mission Control AI — AgroSat[/bold]\n"
        f"[{COR_MUTED}]Global Solution 2026.1 · FIAP · Ciência da Computação[/]\n\n"
        "[bold]Trilha:[/bold] 🌾 AgroSat — Sensoriamento Agrícola Orbital\n"
        "[bold]Satélite simulado:[/bold] AgroSat-1 (LEO 650km, similar ao CBERS-4A)\n"
        "[bold]Modelo de IA:[/bold] gpt-oss:120b via Ollama Cloud\n\n"
        "[bold]Parâmetros monitorados:[/bold]\n"
        "  • Saúde do Sensor NDVI (%)\n"
        "  • Temperatura do Payload Óptico (°C)\n"
        "  • Armazenamento Disponível (%)\n"
        "  • Janela de Downlink (min)\n"
        "  • Estabilidade de Atitude (°)\n\n"
        "[bold]Impacto terrestre:[/bold] Agronegócio brasileiro — gestão de safras,\n"
        "irrigação inteligente e seguro rural baseado em índice de vegetação."
    )
    console.print(Panel(
        texto,
        title=f"[bold {COR_ROXO}]◆ Sobre o Projeto[/]",
        border_style=COR_ROXO,
        padding=(1, 2),
    ))
    console.print()


# ──────────────────────────────────────────────────────────
# Loop principal da CLI
# ──────────────────────────────────────────────────────────

def run_cli(engine):
    """Loop principal da CLI — recebe input, despacha para o engine."""
    show_banner()

    # Avisa se o engine ainda não está implementado
    if not engine.is_ready():
        show_info(
            "⚠  Engine status: AGUARDANDO IMPLEMENTAÇÃO ✗\n"
            "   Complete src/engine.py, src/telemetria.py e src/alertas.py.",
            estilo="yellow"
        )

    while True:
        try:
            user_input = session.prompt("❯ ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[{COR_MUTED}]Sessão encerrada. Até logo! 🛰[/]\n")
            break

        if not user_input:
            continue

        # ── Comandos especiais ────────────────────────────
        cmd = user_input.lower()

        if cmd == "/exit":
            console.print(f"\n[{COR_MUTED}]Mission Control AI desconectado. 🌾[/]\n")
            break

        elif cmd == "/help":
            show_help()

        elif cmd == "/about":
            show_about()

        elif cmd == "/clear":
            show_banner()

        elif cmd == "/status":
            console.print(f"  [{COR_MUTED}]Coletando telemetria...[/]\n")
            snapshot = engine.status_snapshot()
            show_response(snapshot, titulo="◆ Status da Missão", nivel=engine._ultimo_nivel)

        elif cmd == "/cenario":
            # Força cenário crítico para demonstração
            console.print(f"  [{COR_ALERTA}]⚠  Simulando cenário de falha crítica...[/]\n")
            from src.telemetria import coletar
            from src.alertas import avaliar, nivel_geral, resumo_alertas

            # Temporariamente força dados críticos e pede análise à IA
            resposta = engine.analyze(
                "ALERTA: detectei múltiplas falhas simultâneas no satélite. "
                "Qual é a situação geral da missão e quais ações devo tomar imediatamente? "
                "Qual o impacto para os produtores rurais que dependem dos nossos dados?"
            )
            show_response(resposta, titulo="◆ Análise de Cenário Crítico", nivel="CRÍTICO")

        else:
            # ── Qualquer outra entrada vai para o motor de análise ──
            console.print(f"  [{COR_MUTED}]Analisando com IA generativa...[/]\n")
            resposta = engine.analyze(user_input)

            # Determina cor com base no último nível detectado
            nivel = getattr(engine, "_ultimo_nivel", "NORMAL")
            show_response(resposta, nivel=nivel)
