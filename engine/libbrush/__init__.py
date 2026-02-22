# engine/libbrush/__init__.py
"""
LibBrush Engine
Pure Python brush engine for Creative Suite image editor.
Provides pressure-sensitive brush strokes with various brush tips.
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Callable
from enum import Enum


class BrushTip(Enum):
    """Available brush tip types."""
    ROUND = "round"
    SQUARE = "square"
    SOFT = "soft"
    AIRBRUSH = "airbrush"


@dataclass
class BrushSettings:
    """Brush configuration settings."""
    size: float = 10.0
    hardness: float = 0.8
    opacity: float = 1.0
    flow: float = 1.0
    spacing: float = 0.25
    tip: BrushTip = BrushTip.ROUND
    color: Tuple[int, int, int, int] = (0, 0, 0, 255)
    pressure_affects_size: bool = True
    pressure_affects_opacity: bool = True


@dataclass
class StrokePoint:
    """A single point in a brush stroke."""
    x: float
    y: float
    pressure: float = 1.0
    timestamp: float = 0.0


@dataclass
class StrokeResult:
    """Result of a stroke operation containing affected pixels."""
    points: List[Tuple[int, int, Tuple[int, int, int, int]]] = field(default_factory=list)
    bounds: Optional[Tuple[int, int, int, int]] = None


class BrushEngine:
    """
    Brush engine for drawing pressure-sensitive strokes.

    Usage:
        engine = BrushEngine()
        engine.set_brush(BrushSettings(size=20, color=(255, 0, 0, 255)))
        engine.begin_stroke()
        result = engine.stroke(100, 100, 0.5)
        result = engine.stroke(110, 105, 0.6)
        engine.end_stroke()
    """

    def __init__(self):
        self._settings = BrushSettings()
        self._stroke_points: List[StrokePoint] = []
        self._is_stroking = False
        self._last_point: Optional[StrokePoint] = None
        self._accumulator: float = 0.0
        self._stroke_callback: Optional[Callable[[StrokeResult], None]] = None

    @property
    def settings(self) -> BrushSettings:
        """Get current brush settings."""
        return self._settings

    def set_brush(self, settings: BrushSettings) -> None:
        """Set brush settings."""
        self._settings = settings

    def set_color(self, r: int, g: int, b: int, a: int = 255) -> None:
        """Set brush color."""
        self._settings.color = (r, g, b, a)

    def set_size(self, size: float) -> None:
        """Set brush size."""
        self._settings.size = max(1.0, size)

    def set_opacity(self, opacity: float) -> None:
        """Set brush opacity (0.0 - 1.0)."""
        self._settings.opacity = max(0.0, min(1.0, opacity))

    def set_hardness(self, hardness: float) -> None:
        """Set brush hardness (0.0 - 1.0)."""
        self._settings.hardness = max(0.0, min(1.0, hardness))

    def set_stroke_callback(self, callback: Callable[[StrokeResult], None]) -> None:
        """Set callback function called after each stroke segment."""
        self._stroke_callback = callback

    def begin_stroke(self) -> None:
        """Begin a new stroke."""
        self._stroke_points.clear()
        self._is_stroking = True
        self._last_point = None
        self._accumulator = 0.0

    def end_stroke(self) -> List[StrokePoint]:
        """End current stroke and return all points."""
        self._is_stroking = False
        points = list(self._stroke_points)
        self._stroke_points.clear()
        self._last_point = None
        return points

    def stroke(self, x: float, y: float, pressure: float = 1.0) -> StrokeResult:
        """
        Add a stroke point and return affected pixels.

        Args:
            x: X coordinate
            y: Y coordinate
            pressure: Pen pressure (0.0 - 1.0)

        Returns:
            StrokeResult containing pixels to draw
        """
        pressure = max(0.0, min(1.0, pressure))
        current = StrokePoint(x, y, pressure)
        self._stroke_points.append(current)

        result = StrokeResult()

        if self._last_point is None:
            # First point - draw a single dab
            result = self._draw_dab(x, y, pressure)
        else:
            # Interpolate between last point and current point
            result = self._interpolate_stroke(self._last_point, current)

        self._last_point = current

        if self._stroke_callback and result.points:
            self._stroke_callback(result)

        return result

    def _draw_dab(self, x: float, y: float, pressure: float) -> StrokeResult:
        """Draw a single brush dab at the given position."""
        result = StrokeResult()

        # Calculate effective size based on pressure
        size = self._settings.size
        if self._settings.pressure_affects_size:
            size *= pressure

        # Calculate effective opacity based on pressure
        base_opacity = self._settings.opacity * self._settings.flow
        if self._settings.pressure_affects_opacity:
            base_opacity *= pressure

        radius = size / 2.0
        if radius < 0.5:
            radius = 0.5

        int_radius = int(math.ceil(radius))
        min_x = int(x - int_radius)
        min_y = int(y - int_radius)
        max_x = int(x + int_radius)
        max_y = int(y + int_radius)

        r, g, b, a = self._settings.color

        for py in range(min_y, max_y + 1):
            for px in range(min_x, max_x + 1):
                # Calculate distance from center
                dx = px - x
                dy = py - y
                dist = math.sqrt(dx * dx + dy * dy)

                if dist <= radius:
                    # Calculate pixel opacity based on brush tip and hardness
                    pixel_opacity = self._calculate_dab_opacity(
                        dist, radius, self._settings.hardness, self._settings.tip
                    )
                    pixel_opacity *= base_opacity

                    if pixel_opacity > 0.01:
                        final_alpha = int(a * pixel_opacity)
                        result.points.append((px, py, (r, g, b, final_alpha)))

        if result.points:
            result.bounds = (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

        return result

    def _calculate_dab_opacity(
        self, dist: float, radius: float, hardness: float, tip: BrushTip
    ) -> float:
        """Calculate opacity for a pixel based on distance from brush center."""
        if dist > radius:
            return 0.0

        normalized_dist = dist / radius

        if tip == BrushTip.ROUND:
            # Hard edge with hardness falloff
            hard_edge = hardness
            if normalized_dist < hard_edge:
                return 1.0
            else:
                # Smooth falloff in outer region
                falloff = (normalized_dist - hard_edge) / (1.0 - hard_edge)
                return 1.0 - falloff

        elif tip == BrushTip.SOFT:
            # Gaussian-like falloff
            sigma = 0.5 * (1.0 - hardness * 0.5)
            return math.exp(-(normalized_dist * normalized_dist) / (2 * sigma * sigma))

        elif tip == BrushTip.AIRBRUSH:
            # Very soft, gradual falloff
            return (1.0 - normalized_dist) ** 2

        elif tip == BrushTip.SQUARE:
            # Square brush - check if within square bounds
            abs_dx = abs(dist)
            if abs_dx <= radius * 0.707:  # sqrt(2)/2
                return 1.0
            return 0.0

        return 1.0 - normalized_dist

    def _interpolate_stroke(
        self, p1: StrokePoint, p2: StrokePoint
    ) -> StrokeResult:
        """Interpolate between two stroke points and draw dabs along the path."""
        result = StrokeResult()

        dx = p2.x - p1.x
        dy = p2.y - p1.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 0.001:
            return result

        # Calculate spacing in pixels
        spacing_pixels = max(1.0, self._settings.size * self._settings.spacing)

        # Start from accumulated distance
        current_dist = self._accumulator

        while current_dist < distance:
            # Interpolation factor
            t = current_dist / distance

            # Interpolate position and pressure
            ix = p1.x + dx * t
            iy = p1.y + dy * t
            ip = p1.pressure + (p2.pressure - p1.pressure) * t

            # Draw dab at interpolated position
            dab_result = self._draw_dab(ix, iy, ip)
            result.points.extend(dab_result.points)

            current_dist += spacing_pixels

        # Store remainder for next segment
        self._accumulator = current_dist - distance

        # Calculate combined bounds
        if result.points:
            xs = [p[0] for p in result.points]
            ys = [p[1] for p in result.points]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            result.bounds = (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

        return result

    def get_stroke_preview(
        self, x: float, y: float, pressure: float = 1.0
    ) -> StrokeResult:
        """
        Get a preview of what a stroke would look like without committing it.
        Useful for showing brush cursor.
        """
        return self._draw_dab(x, y, pressure)


# Convenience functions for quick brush creation
def create_round_brush(size: float = 10, color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> BrushEngine:
    """Create a basic round brush."""
    engine = BrushEngine()
    engine.set_brush(BrushSettings(
        size=size,
        color=color,
        tip=BrushTip.ROUND,
        hardness=0.9
    ))
    return engine


def create_soft_brush(size: float = 20, color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> BrushEngine:
    """Create a soft-edged brush."""
    engine = BrushEngine()
    engine.set_brush(BrushSettings(
        size=size,
        color=color,
        tip=BrushTip.SOFT,
        hardness=0.3
    ))
    return engine


def create_airbrush(size: float = 30, color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> BrushEngine:
    """Create an airbrush."""
    engine = BrushEngine()
    engine.set_brush(BrushSettings(
        size=size,
        color=color,
        tip=BrushTip.AIRBRUSH,
        hardness=0.1,
        flow=0.3
    ))
    return engine
