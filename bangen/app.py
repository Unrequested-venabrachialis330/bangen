"""Bangen v2 — entry point."""

from __future__ import annotations


def main() -> None:
    from bangen.cli.parser import app as cli_app
    from bangen.cli.parser import has_cli_args

    if has_cli_args():
        cli_app()
    else:
        from bangen.presets.manager import PresetManager
        from bangen.rendering.engine import RenderEngine
        from bangen.tui.app import TUIApp

        engine = RenderEngine()
        pm = PresetManager()
        tui_app = TUIApp(engine, pm)
        tui_app.run()
