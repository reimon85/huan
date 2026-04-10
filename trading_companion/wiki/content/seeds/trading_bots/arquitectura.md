---
title: Arquitectura de Trading Bots
type: topic
branch: trading_bots
tags: arquitectura,bot,automatizacion,sistema
summary: Diseño y arquitectura de sistemas automatizados de trading
---

# Arquitectura de Trading Bots

Un trading bot es un sistema automatizado que ejecuta operaciones de trading basándose en lógica predefinida, sin intervención humana constante.

## Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                      TRADING BOT                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Data    │  │  Signal  │  │ Portfolio│  │ Execution│    │
│  │  Feed    │→ │  Engine   │→ │  Manager │→ │  Engine  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│       ↓              ↓             ↓             ↓        │
│  ┌──────────────────────────────────────────────────┐     │
│  │              Risk Management Layer               │     │
│  └──────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## 1. Data Feed (Fuente de Datos)

### Responsabilidades

- Conexión a exchanges/brokers
- Obtención de datos de mercado en tiempo real
- Normalización de formatos de datos
- Manejo de reconexiones

### Tipos de Datos

| Tipo | Frecuencia | Uso |
|------|------------|-----|
| **Tick** | Microsegundos | Alta frecuencia |
| **OHLCV** | 1min-1día | Análisis, señales |
| **Order Book** | Tiempo real | Market making |
| **Trades** | Streaming | Confirmación |

### Implementación

```python
class DataFeed:
    """Base class for data feeds."""

    def __init__(self, api_client, symbols: list[str]):
        self.api_client = api_client
        self.symbols = symbols
        self._running = False
        self._callbacks: list[callable] = []

    async def start(self) -> None:
        """Start consuming data."""
        self._running = True
        asyncio.create_task(self._consume_loop())

    async def stop(self) -> None:
        """Stop consuming data."""
        self._running = False

    def subscribe(self, callback: callable) -> None:
        """Subscribe to data updates."""
        self._callbacks.append(callback)

    async def _consume_loop(self) -> None:
        """Main data consumption loop."""
        while self._running:
            try:
                data = await self._fetch_data()
                for callback in self._callbacks:
                    await callback(data)
            except ConnectionError:
                await self._reconnect()
            except Exception as e:
                logging.error(f"Data feed error: {e}")

    async def _fetch_data(self) -> dict:
        """Fetch new data from source."""
        raise NotImplementedError

    async def _reconnect(self) -> None:
        """Handle reconnection logic."""
        await asyncio.sleep(5)
```

## 2. Signal Engine (Motor de Señales)

### Responsabilidades

- Procesar datos de mercado
- Aplicar estrategias/indicadores
- Generar señales de trading
- Filtrar señales por criterios

### Arquitectura

```python
class SignalEngine:
    """
    Processes market data and generates trading signals.
    """

    def __init__(self, strategies: list[Strategy]):
        self.strategies = strategies
        self.signals: deque = deque(maxlen=1000)

    async def process(self, market_data: MarketData) -> list[Signal]:
        """
        Process market data and generate signals.

        Args:
            market_data: Current market data snapshot

        Returns:
            List of generated signals
        """
        signals = []

        for strategy in self.strategies:
            if strategy.should_evaluate(market_data):
                signal = await strategy.evaluate(market_data)
                if signal:
                    signals.append(signal)

        # Filter signals
        filtered = self._filter_signals(signals)

        # Store signals
        self.signals.extend(filtered)

        return filtered

    def _filter_signals(self, signals: list[Signal]) -> list[Signal]:
        """Apply filters to signals."""
        # Remove conflicting signals
        # Apply momentum filters
        # Check correlations
        return signals
```

## 3. Portfolio Manager (Gestor de Cartera)

### Responsabilidades

- Calcular tamaños de posición
- Gestionar el capital disponible
- Balancear exposiciones
- Tracking de P&L

### Position Sizing

```python
@dataclass
class Position:
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    side: PositionSide

    @property
    def pnl(self) -> float:
        if self.side == PositionSide.LONG:
            return (self.current_price - self.entry_price) * self.quantity
        return (self.entry_price - self.current_price) * self.quantity

    @property
    def pnl_percent(self) -> float:
        if self.entry_price == 0:
            return 0.0
        return (self.pnl / (self.entry_price * self.quantity)) * 100


class PortfolioManager:
    """Manages positions and portfolio-level concerns."""

    def __init__(
        self,
        initial_capital: float,
        max_position_size: float = 0.1,
        max_total_exposure: float = 0.5
    ):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: dict[str, Position] = {}
        self.max_position_size = max_position_size
        self.max_total_exposure = max_total_exposure

    @property
    def total_equity(self) -> float:
        return self.cash + sum(p.pnl for p in self.positions.values())

    @property
    def total_exposure(self) -> float:
        positions_value = sum(
            p.current_price * p.quantity
            for p in self.positions.values()
        )
        return positions_value / self.initial_capital

    def can_open_position(self, symbol: str, value: float) -> bool:
        """Check if we can open a new position."""
        # Check position limit
        if symbol in self.positions:
            return False

        # Check position size limit
        if value > self.initial_capital * self.max_position_size:
            return False

        # Check total exposure limit
        new_exposure = (self._positions_value() + value) / self.initial_capital
        if new_exposure > self.max_total_exposure:
            return False

        # Check cash
        if value > self.cash:
            return False

        return True

    def calculate_position_size(
        self,
        account_balance: float,
        risk_per_trade: float,
        entry_price: float,
        stop_loss: float
    ) -> float:
        """
        Calculate optimal position size based on risk parameters.
        """
        risk_amount = account_balance * risk_per_trade
        risk_per_unit = abs(entry_price - stop_loss)
        return risk_amount / risk_per_unit

    def open_position(
        self,
        symbol: str,
        quantity: float,
        price: float,
        side: PositionSide
    ) -> Position:
        """Open a new position."""
        position = Position(
            symbol=symbol,
            quantity=quantity,
            entry_price=price,
            current_price=price,
            side=side
        )
        self.positions[symbol] = position
        self.cash -= price * quantity
        return position

    def close_position(self, symbol: str) -> float:
        """Close an existing position and return P&L."""
        if symbol not in self.positions:
            raise ValueError(f"No position found for {symbol}")

        position = self.positions[symbol]
        self.cash += position.current_price * position.quantity
        pnl = position.pnl

        del self.positions[symbol]
        return pnl

    def _positions_value(self) -> float:
        """Calculate total value of all positions."""
        return sum(p.current_price * p.quantity for p in self.positions.values())
```

## 4. Execution Engine (Motor de Ejecución)

### Responsabilidades

- Enviar órdenes a brokers/exchanges
- Manejar tipos de órdenes
- Optimizar ejecución
- Manejar fills y confirmaciones

### Tipos de Ejecución

```python
class ExecutionEngine:
    """Handles order execution."""

    def __init__(self, broker: BrokerAdapter):
        self.broker = broker
        self.pending_orders: dict[str, Order] = {}

    async def execute_signal(
        self,
        signal: Signal,
        portfolio: PortfolioManager
    ) -> OrderResult:
        """
        Execute a trading signal.

        Args:
            signal: Signal to execute
            portfolio: Portfolio manager for sizing

        Returns:
            Result of the execution
        """
        # Calculate position size
        position_size = portfolio.calculate_position_size(
            account_balance=portfolio.total_equity,
            risk_per_trade=signal.risk_percent,
            entry_price=signal.price,
            stop_loss=signal.stop_loss
        )

        # Determine order type based on urgency
        order_type = self._select_order_type(signal)

        # Create order
        order = Order(
            symbol=signal.symbol,
            side=signal.side,
            quantity=position_size,
            order_type=order_type,
            price=signal.price if order_type in [OrderType.LIMIT, OrderType.STOP] else None,
            stop_price=signal.stop_loss if order_type == OrderType.STOP else None
        )

        # Submit order
        result = await self._submit_order(order)
        return result

    def _select_order_type(self, signal: Signal) -> OrderType:
        """Select optimal order type based on conditions."""
        if signal.urgency == Urgency.HIGH:
            return OrderType.MARKET
        elif signal.urgency == Urgency.NORMAL:
            return OrderType.LIMIT
        else:
            return OrderType.STOP_LIMIT
```

## 5. Risk Management Layer

### Componentes

```python
class RiskManager:
    """Centralized risk management."""

    def __init__(self, config: RiskConfig):
        self.max_daily_loss = config.max_daily_loss
        self.max_drawdown = config.max_drawdown
        self.max_positions = config.max_positions
        self.daily_loss = 0.0

    def pre_trade_check(
        self,
        signal: Signal,
        portfolio: PortfolioManager
    ) -> tuple[bool, str]:
        """
        Pre-trade risk checks.

        Returns:
            (allowed, reason_if_not_allowed)
        """
        # Check daily loss limit
        if self.daily_loss >= self.max_daily_loss:
            return False, "Daily loss limit reached"

        # Check drawdown limit
        drawdown = self._calculate_drawdown(portfolio)
        if drawdown >= self.max_drawdown:
            return False, "Max drawdown limit reached"

        # Check position count
        if len(portfolio.positions) >= self.max_positions:
            return False, "Max positions reached"

        # Check correlation
        if self._high_correlation(signal, portfolio):
            return False, "High correlation with existing positions"

        return True, ""

    def post_trade_update(self, trade_result: TradeResult) -> None:
        """Update risk metrics after trade."""
        if trade_result.pnl < 0:
            self.daily_loss += abs(trade_result.pnl)

    def _calculate_drawdown(self, portfolio: PortfolioManager) -> float:
        """Calculate current drawdown."""
        peak = portfolio.initial_capital  # Simplified
        current = portfolio.total_equity
        return (peak - current) / peak

    def _high_correlation(self, signal: Signal, portfolio: PortfolioManager) -> bool:
        """Check correlation with existing positions."""
        # Simplified check
        return False
```

## Patrones Arquitectónicos

### Event-Driven Architecture

```python
class EventBus:
    """Centralized event bus for component communication."""

    def __init__(self):
        self._subscribers: dict[str, list[callable]] = {}

    def publish(self, event_type: str, data: any) -> None:
        """Publish an event."""
        for callback in self._subscribers.get(event_type, []):
            callback(data)

    def subscribe(self, event_type: str, callback: callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)


# Event types
class Events:
    NEW_DATA = "new_data"
    SIGNAL_GENERATED = "signal_generated"
    ORDER_SUBMITTED = "order_submitted"
    ORDER_FILLED = "order_filled"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    RISK_TRIGGERED = "risk_triggered"
```

### State Machine para Orders

```
                    ┌──────────┐
         ┌─────────│ PENDING  │─────────┐
         │         └──────────┘         │
         │                               │
         ▼                               ▼
    ┌─────────┐                   ┌──────────┐
    │ FILLED  │                   │ REJECTED │
    └─────────┘                   └──────────┘
         │
         ▼
    ┌──────────┐         ┌──────────┐
    │ PARTIAL  │────────│ COMPLETE │
    └──────────┘         └──────────┘
         │                     ▲
         ▼                     │
    ┌──────────┐               │
    │ CANCELLED│───────────────┘
    └──────────┘
```

## Consideraciones de Diseño

### Latencia

| Componente | Latencia Típica |
|------------|-----------------|
| Data Feed | 1-100ms |
| Signal Gen | 1-10ms |
| Risk Check | 0.1-1ms |
| Order Entry | 1-50ms |
| Exchange Fill | 5-200ms |

### Throughput

- HFT: >100,000 orders/segundo
- Alta frecuencia: 1,000-100,000/segundo
- Baja frecuencia: <1,000/segundo

### Fiabilidad

- Graceful degradation
- Circuit breakers
- Dead letter queues para mensajes fallidos
- Persistencia del estado
