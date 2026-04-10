---
title: Marco Legal de Trading
type: topic
branch: regulacion
tags: regulacion,legal,compliance,SEC,FINRA
summary: Regulaciones y marcos legales que gobiernan las actividades de trading
---

# Marco Legal de Trading

El trading está sujeto a extensive regulación para proteger inversores, mantener integridad del mercado y prevenir fraude. Los requisitos varían por jurisdicción pero comparten principios fundamentales.

## Principales Reguladores Globales

### América

| Regulador | Jurisdicción | Focus Principal |
|-----------|--------------|-----------------|
| **SEC** | Estados Unidos | Valores, protección inversores |
| **FINRA** | Estados Unidos | Broker-dealers, miembros NYSE |
| **CFTC** | Estados Unidos | Commodities, futuros |
| **CVM** | Brasil | Mercados de capitais |
| **CNV** | Argentina | Mercado de valores |

### Europa

| Regulador | Jurisdicción | Focus Principal |
|-----------|--------------|-----------------|
| **ESMA** | Unión Europea | Mercados, MiFID II |
| **FCA** | Reino Unido | Conducta, mercados |
| **BaFin** | Alemania | Banca, seguros |
| **AMF** | Francia | Mercados financieros |

### Asia-Pacífico

| Regulador | Jurisdicción |
|-----------|--------------|
| **FSA** | Japón |
| **ASIC** | Australia |
| **MAS** | Singapur |
| **SEBI** | India |

## Regulación Estadounidense (SEC)

### Securities Act of 1933

- Requiere registro de nuevos valores
- Prohíbe fraude en venta de valores
- Requiere disclosure completo

### Securities Exchange Act of 1934

- Regulación de exchanges y brokers
- Supervision de short selling
- Reglas contra manipulación

### Regla 10b-5

Prohíbe cualquier acto o práctica fraudulenta en conexión con la compra o venta de valores.

```python
# Ejemplo de prácticas que podrían violar 10b-5:
PROHIBITED_PRACTICES = [
    "Material misstatements or omissions",
    "Insider trading based on non-public information",
    "Market manipulation schemes",
    "Fraudulent devices or schemes",
    "Any act which operates as fraud or deceit"
]
```

## Normas de Conducta

### Suitable Recommendations (Suitability)

Los brokers deben tener basis razonable para creer que una recomendación es adecuada para el cliente.

**Factores a Considerar**:

```python
SUITABILITY_FACTORS = {
    "customer": {
        "age": "Edad del cliente",
        "tax_bracket": "Situación fiscal",
        "investment_objectives": "Objetivos (income, growth, preservation)",
        "risk_tolerance": "Tolerancia al riesgo",
        "time_horizon": "Horizonte temporal",
        "liquidity_needs": "Necesidades de liquidez",
        "existing_holdings": "Portafolio actual"
    },
    "recommendation": {
        "risks": "Riesgos del instrumento",
        "volatility": "Volatilidad esperada",
        "liquidity": "Liquidez del instrumento",
        "complexity": "Complejidad"
    }
}
```

### Best Execution

Los brokers deben buscar el mejor resultado razonablemente disponible para el cliente.

**Criterios de Best Execution**:

| Criterio | Descripción |
|----------|-------------|
| **Price** | Mejor precio disponible |
| **Size** | Tamaño de la orden |
| **Speed** | Velocidad de ejecución |
| ** Likelihood** | Probabilidad de ejecución |
| **Cost** | Costos de transacción |

## Trading con Información Privilegiada

### Insider Trading

> "Trading en valores basándose en información material no pública."

### Tipos de Información Privilegiada

```python
class InsiderInformation:
    """
    Clasificación de información privilegiada.
    """

    MATERIAL = "Material"  # Reasonable investor would consider important
    NON_PUBLIC = "Non-Public"  # Not available to the general public

    # Ejemplos de información material:
    EXAMPLES = [
        "Earnings announcements (positive or negative)",
        "Merger and acquisition discussions",
        "Changes in senior leadership",
        "Regulatory actions",
        "Major contract wins or losses",
        "Financial restatements",
        "Product launches or failures"
    ]

    # Violations penalties:
    PENALTIES = {
        "criminal": {
            "jail": "Up to 20 years",
            "fine": "Up to $5 million for individuals"
        },
        "civil": {
            "disgorgement": "Return profits",
            "penalty": "Up to 3x profits gained"
        },
        "regulatory": {
            "trading_ban": "Permanent bar from industry",
            "license_revocation": "Termination of registration"
        }
    }
```

## Regulación de Brokers/Dealers

### Registro y Licencia

```python
REQUIRED_LICENSES = {
    "Series 7": "General Securities Representative - Can buy/sell most securities",
    "Series 63": "Uniform Securities Agent - State-level registration",
    "Series 65": "Uniform Investment Adviser - Fee-based advice",
    "Series 66": "Combined 63 + 65",
    "Series 3": "Commodities (NCUA)",
    "Series 9/10": "Supervisory and management"
}
```

### net Capital Rule (Rule 15c3-1)

Los broker-dealers deben mantener net capital mínimo.

```python
class NetCapitalRequirements:
    """
    Requisitos de net capital según tipo de firma.
    """

    # Capital mínimo según volumen de negocio
    MINIMUM_CAPITAL = {
        "introducing_broker": 50_000,  # $50,000 mínimo
        "clearing_broker": 250_000,   # $250,000 mínimo
        "market_maker": 1_000_000     # $1M mínimo
    }

    # Ratio de capital líquido
    LIQUID_CAPITAL_RATIO = 0.20  # 20% de debentures debe ser líquido
```

## Day Trading Regulations

### Pattern Day Trader (PDT) Rule

**Definición**: Persona que ejecuta 4+ day trades en 5 días hábiles usando margen.

```python
class PDTRule:
    """
    Regulación para Pattern Day Traders.
    """

    CRITERIA = {
        "day_trades": 4,  # Mínimo de day trades
        "period": 5,  # Días hábiles consecutivos
        "margin_account": True,  # Debe ser cuenta de margen
        "calculation": "Day trades / Net trades in same week"
    }

    REQUIREMENTS = {
        "min_equity": 25_000,  # Equity mínimo en la cuenta
            "equity_definition": "Cash + Long stock value",
            "must_maintain": "Always maintain $25k"
    }

    CONSEQUENCES = {
        "pattern_identified": "Marked as PDT in system",
        "restriction": "Limited to 4:1 intraday buying power",
        "margin_calls": "Can trigger margin calls faster"
    }
```

## Short Selling Regulations

### Regulation SHO

```python
REG_SHO_RULES = {
    "locate_requirement": "Must locate borrowable shares before shorting",
    "closeout_requirement": "Must close short positions within T+13 days",
    "restricted_list": "Cannot short stocks on threshold lists",
    "uptick_rule": "Can only short at higher price than previous sale"
}
```

### Fail to Deliver

```python
class FailToDeliver:
    """
    Cuando vendedor no entrega acciones.
    """

    THRESHOLDS = {
        "threshold_security": "5 consecutive settlement fails",
        "closeout_period": "T+13 from trade date"
    }

    CONSEQUENCES = {
        "buying_restriction": "Cannot facilitate short selling",
        "forced_close": "Broker must close position",
        "reporting": "Must be reported to SEC"
    }
```

## MIFID II (Europa)

### Principios Clave

| Requisito | Descripción |
|-----------|-------------|
| **Best Execution** | Documentar y demostrar mejor ejecución |
| **Transaction Reporting** | Reportar todas las transacciones |
| **Product Governance** | Productos adecuados para clientes |
| **Inducements** | Sin pagos por recomendar productos |
| **Record Keeping** | Registrar todas las comunicaciones |

### MiFID II Requirements

```python
MIFID_II_REQUIREMENTS = {
    "client_categorization": {
        "retail": "Maximum protection",
        "professional": "Standard protection",
        "eligible_counterparty": "Minimal protection"
    },

    "suitability_assessment": {
        "knowledge": "Client's investment knowledge",
        "experience": "Experience with types of instruments",
        "financial": "Financial situation",
        "objectives": "Investment objectives"
    },

    "product_intervention": {
        "priciing": "ESMA can intervene on products",
        "distribution": "Can restrict distribution",
        "leverage": "Limits on CFD, forex leverage"
    }
}
```

## Cumplimiento y Supervisión

### Elements of Compliance Program

```python
COMPLIANCE_PROGRAM = {
    "policies": [
        "Written supervisory procedures",
        "Code of conduct",
        "Insider trading policy",
        "Anti-money laundering (AML)",
        "Know Your Customer (KYC)"
    ],

    "surveillance": [
        "Trade monitoring systems",
        "Communication surveillance",
        "Market manipulation detection",
        "Unusual activity alerts"
    ],

    "training": [
        "Annual compliance training",
        "Ethics training",
        "Product-specific training",
        "Regulatory updates"
    ],

    "testing": [
        "Internal audits",
        "Self-regulatory organization reviews",
        "SEC/FCA examinations"
    ]
}
```

## Tax Implications

### Estados Unidos

| Tipo | Rate | Notes |
|------|------|-------|
| Short-term capital gains | Ordinary income | Held < 1 year |
| Long-term capital gains | 0-20% | Held > 1 year |
| Section 1256 contracts | 60/40 split | Options, futures |
| Wash sale | Disallowed | 30-day rule |

### Wash Sale Rule

```python
WASH_SALE_RULE = {
    "definition": "Selling at loss and repurchasing within 30 days",
    "effect": "Loss disallowed and added to new position's cost basis",
    "period": "30 days before AND after sale",
    "scope": "Substantially identical securities"
}
```

## Documentación Requerida

### Para Traders Individuales

```python
REQUIRED_DOCUMENTATION = {
    "account": [
        "Account application",
        "W-9 or W-8BEN (tax forms)",
        "Risk acknowledgment",
        "Margin agreement (if applicable)"
    ],

    "trades": [
        "Trade confirmations (automated)",
        "Monthly statements",
        "Annual 1099 tax form",
        "Cost basis records"
    ],

    "recordkeeping": {
        "duration": "7 years minimum",
        "includes": [
            "All trade records",
            "Communications",
            "Research and recommendations",
            "Compliance records"
        ]
    }
}
```

## Protecciones al Inversor

### SIPC Protection

```python
SIPC_PROTECTION = {
    "coverage": 500_000,
    "cash_limit": 250_000,
    "purpose": "Protection against broker failure",
    "not_covered": [
        "Market losses",
        "Poor investment decisions",
        "Fraud by the investor"
    ]
}
```

## Mejores Prácticas de Cumplimiento

1. **Conocer las reglas** de tu jurisdicción
2. **Documentar todo** - si no está documentado, no pasó
3. **Separación de duties** - no controlar trading y compliance
4. **Training continuo** - las regulaciones cambian
5. **Reporting proactivo** - reportar anomalías
6. **Technology** - sistemas de supervisión
7. **Culture** - tono desde arriba sobre compliance

## Conclusión

> "The law is not made for the protection of experts, but for the public—that is, for lay investors."
> — SEC v. Texas Gulf Sulphur Co.

El conocimiento del marco legal no solo evita sanciones sino que también protege al trader de situaciones problemáticas y mejora la calidad de las decisiones de inversión.
