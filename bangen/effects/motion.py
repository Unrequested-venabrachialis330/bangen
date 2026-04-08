"""Motion-tier effects rewritten for bounded, deterministic transforms."""

from __future__ import annotations

import math

from bangen.effects.base import Effect
from bangen.effects.utils import (
    canvas_to_lines,
    empty_canvas,
    padded_lines,
    place,
    quantized_time,
    signed_noise,
)


def _bounded_offset(value: float, limit: int) -> int:
    if limit <= 0:
        return 0
    return max(-limit, min(limit, round(value)))


def _translate(lines: list[str], dx: int, dy: int) -> list[str]:
    padded, width, height = padded_lines(lines)
    canvas = empty_canvas(width, height)
    for row, line in enumerate(padded):
        for col, char in enumerate(line):
            if char != " ":
                place(canvas, col + dx, row + dy, char)
    return canvas_to_lines(canvas)


class WaveEffect(Effect):
    tier = "motion"

    @property
    def name(self) -> str:
        return "wave"

    def apply(self, lines: list[str], t: float) -> list[str]:
        padded, width, _ = padded_lines(lines)
        if width == 0:
            return lines
        max_offset = max(1, min(6, width // 6))
        result: list[str] = []
        for row, line in enumerate(padded):
            phase = (row * self.config.frequency * 0.85) + (t * self.config.speed * 1.8)
            offset = _bounded_offset(
                math.sin(phase) * self.config.amplitude, max_offset
            )
            if offset > 0:
                result.append((" " * offset + line)[:width])
            elif offset < 0:
                result.append(line[-offset:] + (" " * (-offset)))
            else:
                result.append(line)
        return result


class VerticalWaveEffect(Effect):
    tier = "motion"

    @property
    def name(self) -> str:
        return "vertical_wave"

    def apply(self, lines: list[str], t: float) -> list[str]:
        padded, width, height = padded_lines(lines)
        if width == 0 or height == 0:
            return lines
        canvas = empty_canvas(width, height)
        max_offset = max(1, min(3, height // 5))
        for col in range(width):
            phase = (col * self.config.frequency * 0.6) + (t * self.config.speed * 1.7)
            offset = _bounded_offset(
                math.sin(phase) * self.config.amplitude, max_offset
            )
            for row in range(height):
                char = padded[row][col]
                if char != " ":
                    place(canvas, col, row + offset, char)
        return canvas_to_lines(canvas)


class BounceEffect(Effect):
    tier = "motion"

    @property
    def name(self) -> str:
        return "bounce"

    def apply(self, lines: list[str], t: float) -> list[str]:
        max_offset = max(1, min(3, self._base_height // 4 if self._base_height else 1))
        dy = _bounded_offset(
            math.sin(t * self.config.speed * math.pi * 1.45) * self.config.amplitude,
            max_offset,
        )
        return _translate(lines, 0, dy)


class ScrollEffect(Effect):
    tier = "motion"

    @property
    def name(self) -> str:
        return "scroll"

    def apply(self, lines: list[str], t: float) -> list[str]:
        padded, width, _ = padded_lines(lines)
        if width == 0:
            return lines
        offset = int(t * self.config.speed * 6.0) % width
        return [line[offset:] + line[:offset] for line in padded]


class DriftEffect(Effect):
    tier = "motion"

    @property
    def name(self) -> str:
        return "drift"

    def apply(self, lines: list[str], t: float) -> list[str]:
        max_dx = max(1, min(4, self._base_width // 8 if self._base_width else 1))
        max_dy = max(1, min(2, self._base_height // 4 if self._base_height else 1))
        dx = _bounded_offset(
            math.sin(t * self.config.speed * 0.9) * self.config.amplitude,
            max_dx,
        )
        dy = _bounded_offset(
            math.cos(t * self.config.speed * 0.6) * (self.config.amplitude * 0.5),
            max_dy,
        )
        return _translate(lines, dx, dy)


class ShakeEffect(Effect):
    tier = "motion"

    @property
    def name(self) -> str:
        return "shake"

    def apply(self, lines: list[str], t: float) -> list[str]:
        tick = quantized_time(t, self.config.speed, rate=12.0)
        magnitude = max(1, min(2, round(self.config.amplitude)))
        dx = _bounded_offset(signed_noise(tick, 1.0) * magnitude, magnitude)
        dy = _bounded_offset(signed_noise(tick, 2.0) * magnitude, magnitude)
        return _translate(lines, dx, dy)
