from dataclasses import dataclass, field
from typing import Deque, List, Tuple, Any
from collections import deque

# MARKO engine types
from live_engine.core.trade_types import TradeIntent
from live_engine.market.types import Bar


@dataclass
class MomentumState:
    closes: Deque[float] = field(default_factory=lambda: deque(maxlen=300))
    rsi: float = 0.0
    macd: float = 0.0
    signal_strength: float = 0.0
    last_decision: str = "WAIT"


class MyMomentumStrategy:
    """
    Minimal momentum test strategy.
    Emits telemetry fields defined in metadata.json.
    """

    def __init__(self, params: dict):
        self.params = params or {}
        self.rsi_period = int(self.params.get("rsi_period", 14))
        self.macd_fast = int(self.params.get("macd_fast", 12))
        self.macd_slow = int(self.params.get("macd_slow", 26))
        self.signal_period = int(self.params.get("signal_period", 9))

    def step(self, bar: Bar, state: MomentumState) -> Tuple[List[Any], MomentumState]:
        if state is None:
            state = MomentumState()

        state.closes.append(float(bar.close))

        closes = list(state.closes)
        state.rsi = self._compute_rsi(closes, self.rsi_period)
        macd, signal = self._compute_macd(closes, self.macd_fast, self.macd_slow, self.signal_period)
        state.macd = macd
        state.signal_strength = macd - signal

        # Basic decision to populate telemetry (no orders by default)
        if state.rsi < 30 and state.signal_strength > 0:
            state.last_decision = "BUY_SIGNAL"
        elif state.rsi > 70 and state.signal_strength < 0:
            state.last_decision = "SELL_SIGNAL"
        else:
            state.last_decision = "WAIT"

        return [], state

    def _compute_rsi(self, closes: List[float], period: int) -> float:
        if len(closes) < period + 1:
            return 0.0
        gains = 0.0
        losses = 0.0
        for i in range(-period, 0):
            delta = closes[i] - closes[i - 1]
            if delta >= 0:
                gains += delta
            else:
                losses += abs(delta)
        if losses == 0:
            return 100.0
        rs = gains / losses
        return 100.0 - (100.0 / (1.0 + rs))

    def _ema_series(self, values: List[float], period: int) -> List[float]:
        if not values:
            return []
        alpha = 2.0 / (period + 1.0)
        ema_vals = [values[0]]
        for value in values[1:]:
            ema_vals.append(alpha * value + (1.0 - alpha) * ema_vals[-1])
        return ema_vals

    def _compute_macd(self, closes: List[float], fast: int, slow: int, signal: int) -> Tuple[float, float]:
        if len(closes) < slow:
            return 0.0, 0.0
        ema_fast = self._ema_series(closes, fast)
        ema_slow = self._ema_series(closes, slow)
        macd_series = [f - s for f, s in zip(ema_fast[-len(ema_slow):], ema_slow)]
        signal_series = self._ema_series(macd_series, signal)
        return macd_series[-1], signal_series[-1]
