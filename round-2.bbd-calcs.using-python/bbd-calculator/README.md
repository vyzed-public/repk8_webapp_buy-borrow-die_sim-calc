# Buy, Borrow, Die Strategy Calculator

A local web application for simulating the "Buy, Borrow, Die" wealth strategy.

**Key Feature:** All financial calculations are performed in auditable Python code (`calculator.py`), 
while the JavaScript frontend handles only UI and visualization.

## Files

```
bbd-calculator/
├── calculator.py      # ← AUDIT THIS: Pure Python financial calculations
├── app.py             # Flask web server (minimal, just routes requests)
├── index.html         # Frontend UI (HTML/CSS/JavaScript + Chart.js)
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

Or simply:

```bash
pip install flask
```

### 2. Run the server

```bash
python app.py
```

### 3. Open in browser

Navigate to: **http://localhost:5000**

## Auditing the Calculations

All financial logic is in `calculator.py`. The file contains:

- **Detailed docstrings** explaining every formula
- **Step-by-step comments** for each calculation phase
- **No external dependencies** — just Python standard library
- **Dataclasses** for clean, typed data structures

### Key Formulas (from `calculator.py`)

```python
# Asset growth
end_asset = start_asset * (1 + investment_growth)

# Interest accrual (capitalized)
interest = start_loan * loan_interest

# Inflation-adjusted borrowing
planned_borrow = annual_borrowing * (1 + inflation) ** (year - 1)

# Leverage constraint
if (end_loan / end_asset) > max_leverage:
    new_borrow = max(0, end_asset * max_leverage - start_loan - interest)

# Net worth
net_worth = end_asset - end_loan

# Real (inflation-adjusted) final value
final_net_worth_real = final_net_worth_nominal / (1 + inflation) ** num_years
```

## Running the Calculator Standalone (No Web UI)

You can run `calculator.py` directly to see results in the terminal:

```bash
python calculator.py
```

This runs a default simulation and prints the year-by-year breakdown.

## API Endpoint

The Flask server exposes a single calculation endpoint:

```
POST /api/calculate
Content-Type: application/json

{
    "initial_investment": 5000000,
    "annual_borrowing": 200000,
    "investment_growth": 8,      // percentage
    "loan_interest": 5,          // percentage
    "inflation": 3,              // percentage
    "max_leverage": 50,          // percentage
    "years": 30
}
```

Response:

```json
{
    "success": true,
    "data": {
        "summary": {
            "final_net_worth_nominal": ...,
            "final_net_worth_real": ...,
            "peak_leverage": ...,
            "total_borrowed": ...,
            "total_interest": ...,
            "constrained_years": ...,
            "is_feasible": true
        },
        "years": [
            { "year": 1, "start_asset": ..., ... },
            ...
        ]
    }
}
```

## Strategy Overview

The **Buy-Borrow-Die** strategy:

1. **BUY** appreciating assets (stocks, real estate, etc.)
2. **BORROW** against them for living expenses (loan proceeds are not taxable income)
3. **DIE** with assets that receive a stepped-up basis under IRC §1014

This allows wealthy individuals to:
- Avoid capital gains tax by never selling
- Access funds without triggering taxable events
- Pass assets to heirs who inherit at current market value (stepped-up basis)

## Disclaimer

This calculator is for **educational purposes only**. It is not financial, tax, legal, 
or investment advice. The Buy-Borrow-Die strategy involves significant risks including 
margin calls, interest rate changes, and policy changes. Consult qualified professionals 
before implementing any wealth strategy.

## License

Public Domain — use freely for any purpose.
