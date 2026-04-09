"""Export engine dispatch and validation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from bangen.export.gif import export_gif, normalize_gif_settings
from bangen.export.png import export_png
from bangen.export.txt import export_txt

if TYPE_CHECKING:
    from bangen.rendering.banner import Banner


class Exporter:
    """Converts a Banner into various output formats."""

    def export_txt(
        self,
        banner: "Banner",
        path: str | Path,
        progress_callback=None,
    ) -> None:
        target = self._prepare_path(path)
        self._validate_banner(banner)
        if progress_callback is not None:
            progress_callback(0.1, "Preparing TXT export")
        target.parent.mkdir(parents=True, exist_ok=True)
        if progress_callback is not None:
            progress_callback(0.65, "Writing TXT file")
        export_txt(target, banner.raw_text())
        if progress_callback is not None:
            progress_callback(1.0, "TXT export complete")

    def export_gif(
        self,
        banner: "Banner",
        path: str | Path,
        duration: float,
        fps: float,
        progress_callback=None,
    ) -> None:
        target = self._prepare_path(path)
        self._validate_banner(banner)
        normalize_gif_settings(duration, fps)
        target.parent.mkdir(parents=True, exist_ok=True)
        export_gif(target, banner, duration, fps, progress_callback=progress_callback)

    def export_png(
        self,
        banner: "Banner",
        path: str | Path,
        progress_callback=None,
    ) -> None:
        target = self._prepare_path(path)
        self._validate_banner(banner)
        if progress_callback is not None:
            progress_callback(0.1, "Preparing PNG export")
        target.parent.mkdir(parents=True, exist_ok=True)
        if progress_callback is not None:
            progress_callback(0.7, "Rasterizing PNG")
        export_png(target, banner)
        if progress_callback is not None:
            progress_callback(1.0, "PNG export complete")

    @staticmethod
    def _prepare_path(path: str | Path) -> Path:
        target = Path(path).expanduser()
        if not str(target):
            raise ValueError("Export path cannot be empty.")
        if target.exists() and target.is_dir():
            raise ValueError(f"Export path points to a directory: {target}")
        return target

    @staticmethod
    def _validate_banner(banner: "Banner") -> None:
        if not banner.lines:
            raise ValueError("Banner has no rendered content to export.")
