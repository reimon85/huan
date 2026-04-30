"""Trading Companion — Screener.

Lightweight market scanner using Yahoo Finance and technical primitives.
Detects setups like range breaks, EMA alignments, key level proximity.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)

# Assets to scan
_SCAN_UNIVERSE = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "AUDUSD": "AUDUSD=X",
    "USDCAD": "USDCAD=X",
    "DXY": "DX-Y.NYB",
    "ES": "ES=F",
    "NQ": "NQ=F",
    "CL": "CL=F",
    "GC": "GC=F",
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
}


@dataclass
class ScanResult:
    asset: str
    price: float
    change_1d_pct: float
    change_5d_pct: float
    volatility_20d: float
    trend: str  # bullish / bearish / sideways
    signals: List[str]
    score: int  # higher = more interesting


def _compute_trend_and_signals(df: pd.DataFrame) -> tuple:
    """Compute trend and detect primitive signals from OHLCV dataframe."""
    if df.empty or len(df) < 50:
        return "insufficient_data", []

    signals = []
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df.get("Volume", pd.Series([0] * len(df)))

    # EMAs
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    ema200 = close.ewm(span=200).mean()

    last_close = close.iloc[-1]
    last_ema20 = ema20.iloc[-1]
    last_ema50 = ema50.iloc[-1]
    last_ema200 = ema200.iloc[-1]

    # Trend
    if last_close > last_ema20 > last_ema50 > last_ema200:
        trend = "bullish"
    elif last_close < last_ema20 < last_ema50 < last_ema200:
        trend = "bearish"
    else:
        trend = "sideways"

    # Signal: EMA alignment (golden cross / death cross)
    ema20_prev = ema20.iloc[-5]
    ema50_prev = ema50.iloc[-5]
    if ema20_prev < ema50_prev and last_ema20 > last_ema50:
        signals.append("golden_cross_20_50")
    if ema20_prev > ema50_prev and last_ema20 < last_ema50:
        signals.append("death_cross_20_50")

    # Signal: Price near 20d high/low (range extremes)
    high_20 = high.iloc[-20:].max()
    low_20 = low.iloc[-20:].min()
    range_20 = high_20 - low_20
    if range_20 > 0:
        proximity_high = (high_20 - last_close) / range_20
        proximity_low = (last_close - low_20) / range_20
        if proximity_low < 0.05:
            signals.append("near_20d_low")
        if proximity_high < 0.05:
            signals.append("near_20d_high")

    # Signal: Range compression (Bollinger Band width)
    std20 = close.iloc[-20:].std()
    bb_width = (std20 * 2) / last_ema20 if last_ema20 else 0
    if bb_width < 0.02:
        signals.append("range_compression")

    # Signal: Volume spike
    avg_vol = volume.iloc[-20:].mean()
    last_vol = volume.iloc[-1]
    if avg_vol > 0 and last_vol > avg_vol * 2:
        signals.append("volume_spike")

    # Signal: Gap
    prev_close = close.iloc[-2] if len(close) > 1 else last_close
    gap = (last_close - prev_close) / prev_close if prev_close else 0
    if abs(gap) > 0.01:
        signals.append(f"gap_{'up' if gap > 0 else 'down'}")

    # Signal: Key level bounce (simple support/resistance using local min/max)
    recent_lows = low.iloc[-20:].nsmallest(3)
    recent_highs = high.iloc[-20:].nlargest(3)
    for lvl in recent_lows:
        if abs(last_close - lvl) / last_close < 0.005:
            signals.append("near_support")
            break
    for lvl in recent_highs:
        if abs(last_close - lvl) / last_close < 0.005:
            signals.append("near_resistance")
            break

    return trend, signals


def scan_universe() -> List[ScanResult]:
    """Scan all tracked assets and return prioritized results."""
    results: List[ScanResult] = []

    for name, ticker in _SCAN_UNIVERSE.items():
        try:
            hist = yf.Ticker(ticker).history(period="3mo", interval="1d")
            if hist.empty or len(hist) < 20:
                continue

            last_close = hist["Close"].iloc[-1]
            prev_close = hist["Close"].iloc[-2]
            close_5d = hist["Close"].iloc[-5]
            change_1d = ((last_close / prev_close) - 1) * 100 if prev_close else 0
            change_5d = ((last_close / close_5d) - 1) * 100 if close_5d else 0
            volatility = hist["Close"].pct_change().iloc[-20:].std() * 100

            trend, signals = _compute_trend_and_signals(hist)

            # Score: more signals = higher priority
            score = len(signals)
            if trend in ("bullish", "bearish"):
                score += 1
            if abs(change_1d) > 2:
                score += 1
            if volatility > 2:
                score += 1

            results.append(ScanResult(
                asset=name,
                price=round(last_close, 4),
                change_1d_pct=round(change_1d, 2),
                change_5d_pct=round(change_5d, 2),
                volatility_20d=round(volatility, 2),
                trend=trend,
                signals=signals,
                score=score,
            ))
        except Exception as e:
            logger.debug("Screener failed for %s: %s", name, e)

    # Sort by score descending
    results.sort(key=lambda r: r.score, reverse=True)
    return results


def format_scan(results: List[ScanResult], top_n: int = 10) -> str:
    """Format scan results for agent consumption."""
    if not results:
        return "No se encontraron oportunidades en el scaneo."

    lines = [f"=== SCREENER — {len(results)} activos escaneados ===\n"]
    for r in results[:top_n]:
        emoji = {"bullish": "🟢", "bearish": "🔴", "sideways": "⚪"}.get(r.trend, "⚪")
        sig_str = ", ".join(r.signals) if r.signals else "ninguna"
        lines.append(
            f"{emoji} {r.asset}: ${r.price} | 1d: {r.change_1d_pct:+.2f}% | 5d: {r.change_5d_pct:+.2f}% | "
            f"Vol: {r.volatility_20d:.1f}% | Score: {r.score} | Señales: {sig_str}"
        )

    return "\n".join(lines)
