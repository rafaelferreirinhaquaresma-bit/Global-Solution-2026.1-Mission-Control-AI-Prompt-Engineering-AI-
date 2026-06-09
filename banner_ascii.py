"""
banner_ascii.py — Gerador de banner ASCII art para Mission Control AI.

Uso:
    python banner_ascii.py              # Banner padrão
    python banner_ascii.py -fonts       # Lista todas as fontes disponíveis
    python banner_ascii.py -font slant -text "Mission Control AI"
    python banner_ascii.py -demo        # Demonstra 8 fontes diferentes
"""

import sys
import pyfiglet
from rich.console import Console
from rich.align import Align
from rich.text import Text

console = Console()


def mostrar_banner(font: str = "ansi_shadow"):
    """Exibe o banner padrão do Mission Control AI."""
    linha1 = pyfiglet.figlet_format("Global Solution", font=font)
    linha2 = pyfiglet.figlet_format("Mission Control AI", font=font)

    console.print(Align.center(Text(linha1, style="bold #A855F7")))
    console.print(Align.center(Text(linha2, style="bold #06B6D4")))
    console.print(Align.center(
        Text("── 2026.1 · Prompt Engineering and AI · FIAP ──",
             style="italic #8484A0")
    ))
    console.print(Align.center(
        Text("🌾 Trilha AgroSat — Sensoriamento Agrícola",
             style="bold #22C55E")
    ))


def listar_fontes():
    """Lista todas as fontes disponíveis no PyFiglet."""
    fontes = pyfiglet.FigletFont.getFonts()
    console.print(f"\n[bold #06B6D4]Fontes disponíveis ({len(fontes)} no total):[/]\n")
    for i, fonte in enumerate(sorted(fontes)):
        console.print(f"  {fonte}", end="\n" if (i + 1) % 4 == 0 else "  ")
    console.print()


def demo_fontes():
    """Demonstra 8 fontes diferentes."""
    fontes_demo = ["ansi_shadow", "slant", "big", "banner3", "doom", "cosmic", "speed", "starwars"]
    for fonte in fontes_demo:
        try:
            texto = pyfiglet.figlet_format("AgroSat", font=fonte)
            console.rule(f"[bold #A855F7]Fonte: {fonte}")
            console.print(Text(texto, style="bold #06B6D4"))
        except Exception:
            console.print(f"[yellow]Fonte '{fonte}' não disponível.[/]")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "-fonts" in args:
        listar_fontes()
    elif "-demo" in args:
        demo_fontes()
    elif "-font" in args:
        idx = args.index("-font")
        font_name = args[idx + 1] if idx + 1 < len(args) else "ansi_shadow"
        texto_custom = " ".join(args[args.index("-text") + 1:]) if "-text" in args else "Mission Control AI"
        resultado = pyfiglet.figlet_format(texto_custom, font=font_name)
        console.print(Text(resultado, style="bold #06B6D4"))
    else:
        mostrar_banner()
