"""Temporal-tier effects."""

from __future__ import annotations

from bangen.effects.base import Effect
from bangen.effects.utils import clamp


class TypewriterEffect(Effect):
    tier = "temporal"

    def __init__(
        self,
        config=None,
        chars_per_second: float = 50.0,
        loop: bool = True,
        pause: float = 0.5,
        **_: object,
    ) -> None:
        super().__init__(config)
        self.chars_per_second = chars_per_second
        self.loop = loop
        self.pause = pause

    @property
    def name(self) -> str:
        return "typewriter"

    def precompute(self, banner) -> None:
        super().precompute(banner)
        self._full_text = "\n".join(self._base_lines)
        self._total_chars = len(self._full_text)

    def apply(self, lines: list[str], t: float) -> list[str]:
        total_chars = self._total_chars
        if total_chars == 0:
            return lines

        typing_time = total_chars / (
            self.chars_per_second * max(self.config.speed, 0.1)
        )
        cycle_time = typing_time + self.pause

        if self.loop:
            t = t % max(cycle_time, 0.001)
        else:
            t = min(t, typing_time)

        if t >= typing_time:
            revealed = total_chars
        else:
            revealed = int((t * self.chars_per_second * self.config.speed) + 0.5)

        visible = self._full_text[:revealed]
        split = visible.split("\n")

        result: list[str] = []
        for row, line in enumerate(lines):
            if row < len(split):
                current = split[row]
                result.append(current + (" " * max(0, len(line) - len(current))))
            else:
                result.append(" " * len(line))
        return result


class FadeInEffect(Effect):
    tier = "temporal"

    @property
    def name(self) -> str:
        return "fade_in"

    def apply(self, lines: list[str], t: float) -> list[str]:
        return lines

    def brightness(
        self,
        t: float,
        *,
        row: int,
        col: int,
        char: str,
        lines: list[str],
    ) -> float:
        del row, col, char, lines
        return clamp(t * self.config.speed * 0.9, 0.0, 1.0)

    def opacity(
        self,
        t: float,
        *,
        row: int,
        col: int,
        char: str,
        lines: list[str],
    ) -> float:
        del row, col, char, lines
        return clamp(t * self.config.speed * 0.9, 0.0, 1.0)


class WipeEffect(Effect):
    tier = "temporal"

    def __init__(
        self,
        config=None,
        direction: str = "horizontal",
        loop: bool = False,
        **_: object,
    ) -> None:
        super().__init__(config)
        self.direction = direction
        self.loop = loop

    @property
    def name(self) -> str:
        return "wipe"

    def precompute(self, banner) -> None:
        super().precompute(banner)
        # Compute the bounding box of visible (non-space) characters so the wipe
        # doesn't spend most of its time "revealing" indentation.
        min_row = None
        max_row = None
        min_col = None
        max_col = None
        for row, line in enumerate(self._base_lines):
            if not line:
                continue
            for col, ch in enumerate(line):
                if ch == " ":
                    continue
                if min_row is None or row < min_row:
                    min_row = row
                if max_row is None or row > max_row:
                    max_row = row
                if min_col is None or col < min_col:
                    min_col = col
                if max_col is None or col > max_col:
                    max_col = col

        self._min_row = min_row if min_row is not None else 0
        self._max_row = (
            max_row if max_row is not None else max(0, len(self._base_lines) - 1)
        )
        self._min_col = min_col if min_col is not None else 0
        self._max_col = max_col if max_col is not None else max(0, self._base_width - 1)

    def apply(self, lines: list[str], t: float) -> list[str]:
        progress = t * self.config.speed
        if self.loop:
            progress = progress % 1.0
        else:
            progress = clamp(progress)

        if self.direction == "vertical":
            start = self._min_row
            height = max(1, (self._max_row - self._min_row) + 1)
            cutoff = start + round(height * progress)
            result: list[str] = []
            for row, line in enumerate(lines):
                if row < start or row > self._max_row:
                    result.append(line)
                elif row < cutoff:
                    result.append(line)
                else:
                    result.append(" " * len(line))
            return result

        result: list[str] = []
        start = self._min_col
        width = max(1, (self._max_col - self._min_col) + 1)
        cutoff_col = start + round(width * progress)
        for line in lines:
            if not line:
                result.append(line)
                continue
            padded = line.ljust(self._base_width)
            cutoff = max(0, min(len(padded), cutoff_col))
            result.append(padded[:cutoff] + (" " * max(0, len(padded) - cutoff)))
        return result


class StaggerEffect(Effect):
    tier = "temporal"

    def __init__(
        self,
        config=None,
        line_delay: float = 0.16,
        chars_per_second: float = 120.0,
        **_: object,
    ) -> None:
        super().__init__(config)
        self.line_delay = line_delay
        self.chars_per_second = chars_per_second

    @property
    def name(self) -> str:
        return "stagger"

    def apply(self, lines: list[str], t: float) -> list[str]:
        result: list[str] = []
        cps = self.chars_per_second * max(self.config.speed, 0.1)

        for row, line in enumerate(lines):
            local_t = max(0.0, t - (row * self.line_delay))
            visible = min(len(line), int(local_t * cps))
            result.append(line[:visible] + (" " * max(0, len(line) - visible)))

        return result
