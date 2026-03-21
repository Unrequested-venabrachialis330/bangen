from __future__ import annotations

import time
from pathlib import Path

import pyfiglet
from rich import box
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

APP_NAME = "Bangen"
DEFAULT_TEXT = "Bangen"
DEFAULT_FONT = "ansi_shadow"
DEFAULT_COLOR = "cyan"

COLORS = ["cyan", "red", "green", "yellow", "magenta"]
PRESET_FONTS = [
    "ansi_shadow",
    "slant",
    "standard",
    "block",
    "big",
    "banner3-D",
    "speed",
    "doom",
    "starwars",
    "small",
    "smslant",
]


def welcome(console: Console) -> None:
    message = (
        "Welcome to Bangen, a terminal ASCII banner generator.\n"
        "Choose a font, pick a color, and render your text inside a panel."
    )
    console.print(
        Panel(
            message,
            title=APP_NAME,
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )


def prompt_text(console: Console) -> str:
    text = Prompt.ask("Text to render", default=DEFAULT_TEXT).strip()
    if not text:
        console.print(f"[yellow]Empty input. Using {DEFAULT_TEXT}.[/yellow]")
        return DEFAULT_TEXT
    return text


def get_all_fonts() -> set[str]:
    try:
        return set(pyfiglet.FigletFont.getFonts())
    except Exception:
        return set(PRESET_FONTS)


def select_font(console: Console) -> str:
    console.print("[bold]Font presets[/bold]")
    for idx, font in enumerate(PRESET_FONTS, start=1):
        console.print(f"{idx}. {font}")

    choice = Prompt.ask("Font (name or number)", default=DEFAULT_FONT).strip()
    if choice.isdigit():
        index = int(choice)
        if 1 <= index <= len(PRESET_FONTS):
            return PRESET_FONTS[index - 1]

    if choice in get_all_fonts():
        return choice

    console.print(f"[yellow]Unknown font '{choice}'. Using {DEFAULT_FONT}.[/yellow]")
    return DEFAULT_FONT


def select_color(console: Console) -> str:
    console.print(f"[bold]Colors[/bold]: {', '.join(COLORS)}")
    choice = Prompt.ask("Color", default=DEFAULT_COLOR).strip().lower()
    if choice in COLORS:
        return choice
    console.print(f"[yellow]Unknown color '{choice}'. Using {DEFAULT_COLOR}.[/yellow]")
    return DEFAULT_COLOR


def select_title(console: Console) -> str | None:
    title = Prompt.ask("Panel title (optional)", default="", show_default=False).strip()
    return title or None


def select_border(console: Console) -> bool:
    return Confirm.ask("Show panel border?", default=True)


def select_animation(console: Console) -> tuple[bool, float]:
    animate = Confirm.ask("Animate line by line?", default=False)
    if not animate:
        return False, 0.0

    default_delay = 0.03
    delay_input = Prompt.ask(
        "Delay per line in seconds", default=f"{default_delay}"
    ).strip()
    try:
        delay = float(delay_input)
        if delay < 0:
            raise ValueError
        return True, delay
    except ValueError:
        console.print(
            f"[yellow]Invalid delay '{delay_input}'. Using {default_delay}.[/yellow]"
        )
        return True, default_delay


def render_banner(text: str, font: str) -> str:
    try:
        figlet = pyfiglet.Figlet(font=font)
    except pyfiglet.FontNotFound:
        figlet = pyfiglet.Figlet(font=DEFAULT_FONT)
    return figlet.renderText(text)


def build_panel(banner: str, color: str, title: str | None, border: bool) -> Panel:
    banner_text = Text(banner.rstrip("\n"), style=color, justify="left", no_wrap=True)
    chosen_box = box.HEAVY if border else getattr(box, "NONE", box.MINIMAL)
    return Panel(
        banner_text,
        title=title,
        border_style=color,
        box=chosen_box,
        padding=(1, 2),
    )


def animate_banner(
    console: Console,
    banner: str,
    color: str,
    title: str | None,
    border: bool,
    delay: float,
) -> None:
    lines = banner.rstrip("\n").splitlines()
    if not lines:
        console.print(build_panel("", color, title, border))
        return

    revealed: list[str] = []
    with Live(console=console, refresh_per_second=30) as live:
        for line in lines:
            revealed.append(line)
            live.update(build_panel("\n".join(revealed), color, title, border))
            time.sleep(delay)


def show_banner(
    console: Console,
    banner: str,
    color: str,
    title: str | None,
    border: bool,
    animate: bool,
    delay: float,
) -> None:
    if animate:
        animate_banner(console, banner, color, title, border, delay)
    else:
        console.print(build_panel(banner, color, title, border))


def maybe_save_banner(console: Console, banner: str) -> None:
    if not Confirm.ask("Save banner to a .txt file?", default=False):
        return

    path_input = Prompt.ask("Output path", default="banner.txt").strip()
    path = Path(path_input).expanduser()
    if path.suffix == "":
        path = path.with_suffix(".txt")
    try:
        path.write_text(banner.rstrip("\n") + "\n", encoding="utf-8")
        console.print(f"[green]Saved to {path}[/green]")
    except OSError as exc:
        console.print(f"[red]Failed to save banner: {exc}[/red]")


def main() -> None:
    console = Console()
    welcome(console)

    text = prompt_text(console)
    font = select_font(console)
    color = select_color(console)
    title = select_title(console)
    border = select_border(console)
    animate, delay = select_animation(console)

    banner = render_banner(text, font)
    show_banner(console, banner, color, title, border, animate, delay)
    maybe_save_banner(console, banner)


if __name__ == "__main__":
    main()
