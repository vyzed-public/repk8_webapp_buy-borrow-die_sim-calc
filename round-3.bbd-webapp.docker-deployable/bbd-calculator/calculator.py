"""
Buy, Borrow, Die Strategy Calculator
=====================================

Pure Python implementation of the financial calculations.
No external dependencies - designed for easy auditing.

Strategy Overview:
    1. BUY appreciating assets
    2. BORROW against them (loan proceeds are not taxable income)
    3. DIE with stepped-up basis (IRC §1014) - heirs inherit at FMV

Annual Simulation Logic:
    For each year:
        1. Assets grow by investment_growth_rate
        2. Existing loan accrues interest at loan_interest_rate
        3. New borrowing = base_borrowing * (1 + inflation)^(year-1)
        4. If (total_loan / assets) > max_leverage:
               Reduce borrowing to maintain max_leverage cap
        5. Net Worth = Assets - Loan

Author: Generated for auditing purposes
License: Public Domain
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class YearResult:
    """Results for a single simulation year."""
    year: int
    start_asset: float
    end_asset: float
    start_loan: float
    new_borrow: float
    interest: float
    end_loan: float
    leverage: float       # end_loan / end_asset (as decimal, e.g., 0.35 = 35%)
    net_worth: float      # end_asset - end_loan
    constrained: bool     # True if borrowing was reduced to meet leverage cap


@dataclass
class SimulationResult:
    """Complete simulation results."""
    years: List[YearResult]
    final_net_worth_nominal: float
    final_net_worth_real: float    # Adjusted for inflation (today's dollars)
    peak_leverage: float
    total_borrowed: float
    total_interest: float
    constrained_years: int
    is_feasible: bool              # True if no years were constrained


def simulate(
    initial_investment: float,
    annual_borrowing: float,
    investment_growth: float,
    loan_interest: float,
    inflation: float,
    max_leverage: float,
    num_years: int
) -> SimulationResult:
    """
    Run the Buy-Borrow-Die simulation.

    Parameters
    ----------
    initial_investment : float
        Starting asset value in dollars (e.g., 5_000_000)
    annual_borrowing : float
        First-year borrowing amount in dollars (e.g., 200_000)
        Subsequent years are adjusted for inflation.
    investment_growth : float
        Annual asset growth rate as decimal (e.g., 0.08 for 8%)
    loan_interest : float
        Annual loan interest rate as decimal (e.g., 0.05 for 5%)
    inflation : float
        Annual inflation rate as decimal (e.g., 0.03 for 3%)
        Used to: (a) increase borrowing each year, (b) deflate final net worth
    max_leverage : float
        Maximum allowed loan-to-asset ratio as decimal (e.g., 0.50 for 50%)
    num_years : int
        Number of years to simulate

    Returns
    -------
    SimulationResult
        Complete simulation results including year-by-year breakdown
    """
    # Validate inputs
    if initial_investment < 0:
        raise ValueError("initial_investment must be non-negative")
    if annual_borrowing < 0:
        raise ValueError("annual_borrowing must be non-negative")
    if not (0 <= investment_growth <= 1):
        raise ValueError("investment_growth must be between 0 and 1")
    if not (0 <= loan_interest <= 1):
        raise ValueError("loan_interest must be between 0 and 1")
    if not (0 <= inflation <= 1):
        raise ValueError("inflation must be between 0 and 1")
    if not (0 < max_leverage <= 1):
        raise ValueError("max_leverage must be between 0 and 1")
    if num_years < 1:
        raise ValueError("num_years must be at least 1")

    years_results: List[YearResult] = []
    
    # State variables
    asset = initial_investment
    loan = 0.0
    
    # Accumulators
    total_borrowed = 0.0
    total_interest = 0.0
    peak_leverage = 0.0
    constrained_years = 0

    for year in range(1, num_years + 1):
        # =====================================================================
        # STEP 1: Record starting values
        # =====================================================================
        start_asset = asset
        start_loan = loan

        # =====================================================================
        # STEP 2: Asset growth
        # Formula: end_asset = start_asset * (1 + growth_rate)
        # =====================================================================
        end_asset = start_asset * (1.0 + investment_growth)

        # =====================================================================
        # STEP 3: Interest accrual on existing loan
        # Formula: interest = start_loan * interest_rate
        # Note: Interest is added to loan balance (capitalized, not paid)
        # =====================================================================
        interest = start_loan * loan_interest

        # =====================================================================
        # STEP 4: Calculate planned borrowing (inflation-adjusted)
        # Formula: planned_borrow = base_borrow * (1 + inflation)^(year - 1)
        # Year 1: base amount
        # Year 2: base * (1 + inflation)
        # Year N: base * (1 + inflation)^(N-1)
        # =====================================================================
        inflation_factor = (1.0 + inflation) ** (year - 1)
        planned_borrow = annual_borrowing * inflation_factor

        # =====================================================================
        # STEP 5: Apply leverage constraint
        # Constraint: end_loan / end_asset <= max_leverage
        # Rearranged: end_loan <= end_asset * max_leverage
        # Where: end_loan = start_loan + interest + new_borrow
        # =====================================================================
        new_borrow = planned_borrow
        potential_loan = start_loan + interest + new_borrow
        constrained = False

        if end_asset > 0 and (potential_loan / end_asset) > max_leverage:
            # Calculate maximum allowable loan
            max_allowed_loan = end_asset * max_leverage
            
            # Reduce borrowing to meet constraint
            # max_allowed_loan = start_loan + interest + new_borrow
            # new_borrow = max_allowed_loan - start_loan - interest
            new_borrow = max(0.0, max_allowed_loan - start_loan - interest)
            potential_loan = start_loan + interest + new_borrow
            constrained = True
            constrained_years += 1

        # =====================================================================
        # STEP 6: Calculate final values for the year
        # =====================================================================
        end_loan = potential_loan
        leverage = end_loan / end_asset if end_asset > 0 else 0.0
        net_worth = end_asset - end_loan

        # Update peak leverage tracker
        peak_leverage = max(peak_leverage, leverage)

        # Accumulate totals
        total_borrowed += new_borrow
        total_interest += interest

        # =====================================================================
        # STEP 7: Record year results
        # =====================================================================
        years_results.append(YearResult(
            year=year,
            start_asset=start_asset,
            end_asset=end_asset,
            start_loan=start_loan,
            new_borrow=new_borrow,
            interest=interest,
            end_loan=end_loan,
            leverage=leverage,
            net_worth=net_worth,
            constrained=constrained
        ))

        # =====================================================================
        # STEP 8: Carry forward to next year
        # =====================================================================
        asset = end_asset
        loan = end_loan

    # =========================================================================
    # Calculate final summary values
    # =========================================================================
    final_net_worth_nominal = years_results[-1].net_worth if years_results else 0.0
    
    # Deflate to today's dollars
    # Formula: real_value = nominal_value / (1 + inflation)^years
    deflation_factor = (1.0 + inflation) ** num_years
    final_net_worth_real = final_net_worth_nominal / deflation_factor

    return SimulationResult(
        years=years_results,
        final_net_worth_nominal=final_net_worth_nominal,
        final_net_worth_real=final_net_worth_real,
        peak_leverage=peak_leverage,
        total_borrowed=total_borrowed,
        total_interest=total_interest,
        constrained_years=constrained_years,
        is_feasible=(constrained_years == 0)
    )


def to_dict(result: SimulationResult) -> dict:
    """
    Convert SimulationResult to a JSON-serializable dictionary.
    
    Useful for API responses.
    """
    return {
        "summary": {
            "final_net_worth_nominal": result.final_net_worth_nominal,
            "final_net_worth_real": result.final_net_worth_real,
            "peak_leverage": result.peak_leverage,
            "total_borrowed": result.total_borrowed,
            "total_interest": result.total_interest,
            "constrained_years": result.constrained_years,
            "is_feasible": result.is_feasible
        },
        "years": [
            {
                "year": yr.year,
                "start_asset": yr.start_asset,
                "end_asset": yr.end_asset,
                "start_loan": yr.start_loan,
                "new_borrow": yr.new_borrow,
                "interest": yr.interest,
                "end_loan": yr.end_loan,
                "leverage": yr.leverage,
                "net_worth": yr.net_worth,
                "constrained": yr.constrained
            }
            for yr in result.years
        ]
    }


# =============================================================================
# Standalone test / example usage
# =============================================================================
if __name__ == "__main__":
    # Example: $5M portfolio, $200K/year spending, 8% growth, 5% loan rate
    result = simulate(
        initial_investment=5_000_000,
        annual_borrowing=200_000,
        investment_growth=0.08,
        loan_interest=0.05,
        inflation=0.03,
        max_leverage=0.50,
        num_years=30
    )

    print("=" * 70)
    print("BUY, BORROW, DIE SIMULATION RESULTS")
    print("=" * 70)
    print(f"{'Feasible:':<25} {'Yes' if result.is_feasible else 'No'}")
    print(f"{'Constrained Years:':<25} {result.constrained_years}")
    print(f"{'Peak Leverage:':<25} {result.peak_leverage:.1%}")
    print(f"{'Total Borrowed:':<25} ${result.total_borrowed:,.0f}")
    print(f"{'Total Interest:':<25} ${result.total_interest:,.0f}")
    print(f"{'Final Net Worth (Nom):':<25} ${result.final_net_worth_nominal:,.0f}")
    print(f"{'Final Net Worth (Real):':<25} ${result.final_net_worth_real:,.0f}")
    print()
    print("-" * 70)
    print(f"{'Year':>4} {'End Asset':>14} {'End Loan':>14} {'Leverage':>10} {'Net Worth':>14}")
    print("-" * 70)
    for yr in result.years:
        flag = " *" if yr.constrained else ""
        print(f"{yr.year:>4} ${yr.end_asset:>12,.0f} ${yr.end_loan:>12,.0f} "
              f"{yr.leverage:>9.1%} ${yr.net_worth:>12,.0f}{flag}")
    print("-" * 70)
    print("* = Borrowing was constrained to meet leverage cap")
