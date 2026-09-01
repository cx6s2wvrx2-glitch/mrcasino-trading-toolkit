from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True, slots=True)
class BrokerPriceSpec:
    """Explicit broker/source price precision.

    No XAUUSD tick size or digit count is assumed by V2. These values must come
    from the actual broker/source metadata used for research or execution.
    """

    broker_name: str
    source_symbol: str
    digits: int
    tick_size: Decimal

    def __post_init__(self) -> None:
        if not self.broker_name.strip():
            raise ValueError("broker_name is required")
        if not self.source_symbol.strip():
            raise ValueError("source_symbol is required")
        if self.digits < 0:
            raise ValueError("digits must be non-negative")
        if self.tick_size <= 0:
            raise ValueError("tick_size must be positive")

    @classmethod
    def from_strings(
        cls,
        *,
        broker_name: str,
        source_symbol: str,
        digits: int,
        tick_size: str,
    ) -> "BrokerPriceSpec":
        try:
            parsed_tick = Decimal(tick_size)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("tick_size must be a valid decimal") from exc
        return cls(
            broker_name=broker_name,
            source_symbol=source_symbol,
            digits=digits,
            tick_size=parsed_tick,
        )


def price_distance_in_ticks(*, price_a: float | str | Decimal, price_b: float | str | Decimal, spec: BrokerPriceSpec) -> Decimal:
    """Return absolute price distance in broker ticks without rounding it away."""
    try:
        a = Decimal(str(price_a))
        b = Decimal(str(price_b))
    except InvalidOperation as exc:
        raise ValueError("prices must be valid decimals") from exc
    return abs(a - b) / spec.tick_size


def is_exact_same_broker_price(*, price_a: float | str | Decimal, price_b: float | str | Decimal, spec: BrokerPriceSpec) -> bool:
    """Exact equality at the broker's declared digit precision.

    This is an observable, not an imbalance rule. A future IMB tolerance must be
    explicitly certified; this function must not be repurposed as a hidden
    tolerance classifier.
    """
    try:
        quantum = Decimal(1).scaleb(-spec.digits)
        a = Decimal(str(price_a)).quantize(quantum)
        b = Decimal(str(price_b)).quantize(quantum)
    except InvalidOperation as exc:
        raise ValueError("prices must be valid decimals") from exc
    return a == b
