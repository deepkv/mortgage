"""
Simple mortgage calculator with optional amortization schedule and inflation adjustment.

Features
--------
- Inputs: loan amount, term in years, optional interest rate.
- Output: monthly payment.
- Optional: print a full month-by-month amortization schedule (`--schedule`).
- Inflation: discount each payment to present value using continuous compounding (`--inflation`).
- Output formatting: tabular with thousand separators and yearly dividers.

Examples
--------
$ python mortgage.py 300000 30
Monthly payment: 833.33

$ python mortgage.py 300000 30 --rate 5.5
Monthly payment: 1703.37

$ python mortgage.py 300000 30 --rate 5.5 --schedule --inflation 3.5
Prints a detailed amortization schedule with real (inflation-adjusted) values.
"""
from __future__ import annotations

import argparse
from typing import Optional
from dataclasses import dataclass
import math


def monthly_payment(principal: float, years: int, annual_rate: float = 0.0) -> float:
    """Compute the monthly payment.

    Parameters
    ----------
    principal : float
        Loan amount (currency units).
    years : int
        Term length in years.
    annual_rate : float, optional
        Annual nominal interest rate as a percentage (e.g., 6.5 for 6.5%).
        Defaults to 0.0 (no interest), matching the minimal requirement.

    Returns
    -------
    float
        Monthly payment as a float.
    """
    if years <= 0:
        raise ValueError("years must be positive")
    months = years * 12

    # Convert percentage to decimal monthly rate
    r = (annual_rate / 100.0) / 12.0

    if r == 0:
        payment = principal / months
    else:
        # Standard fixed-rate amortization formula
        factor = (1 + r) ** months
        payment = principal * (r * factor) / (factor - 1)

    return payment


def amortization_schedule(
    principal: float,
    years: int,
    annual_rate: float = 0.0,
    inflation_rate: float = 0.0,
):
    """Yield an amortization schedule month by month.

    Yields dicts with keys: month (1-based), payment, interest, principal, balance.
    """
    if years <= 0:
        raise ValueError("years must be positive")
    months = years * 12
    r = (annual_rate / 100.0) / 12.0
    ia = inflation_rate / 100.0

    pmt = monthly_payment(principal, years, annual_rate)
    balance = float(principal)

    for m in range(1, months + 1):
        if r == 0:
            interest = 0.0
        else:
            interest = balance * r
        principal_component = pmt - interest
        # Guard against tiny negative due to floating point in the last row
        if principal_component > balance:
            principal_component = balance
            pmt_effective = interest + principal_component
        else:
            pmt_effective = pmt
        balance -= principal_component
        # Avoid -0.00 displays
        if abs(balance) < 1e-8:
            balance = 0.0

        # Discount to present value using continuous compounding; time in years = m/12
        if ia == 0:
            discount = 1.0
        else:
            discount = math.exp(-ia * (m / 12.0))

        payment_real = pmt_effective * discount
        interest_real = interest * discount
        principal_real = principal_component * discount

        yield {
            "month": m,
            "payment": pmt_effective,
            "interest": interest,
            "principal": principal_component,
            "balance": balance,
            "discount": discount,
            "payment_real": payment_real,
            "interest_real": interest_real,
            "principal_real": principal_real,
        }


def _inflation_enabled(inflation: float) -> bool:
    return bool(inflation) and inflation != 0.0


def _schedule_header(with_inflation: bool) -> str:
    if with_inflation:
        return f"{'Month':>5} {'Payment':>12} {'Interest':>12} {'Principal':>12} {'Balance':>12} {'Discount':>10} {'Pay.Real':>12} {'Int.Real':>12} {'Prin.Real':>12}"
    return f"{'Month':>5} {'Payment':>12} {'Interest':>12} {'Principal':>12} {'Balance':>12}"


def _format_row(row: dict, with_inflation: bool) -> str:
    if with_inflation:
        return (
            f"{row['month']:5d} {row['payment']:12,.0f} {row['interest']:12,.0f} "
            f"{row['principal']:12,.0f} {row['balance']:12,.0f} {row['discount']:10.6f} "
            f"{row['payment_real']:12,.0f} {row['interest_real']:12,.0f} {row['principal_real']:12,.0f}"
        )
    return (
        f"{row['month']:5d} {row['payment']:12,.0f} {row['interest']:12,.0f} "
        f"{row['principal']:12,.0f} {row['balance']:12,.0f}"
    )


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple mortgage calculator")
    parser.add_argument("loan", type=float, help="Loan amount (e.g., 300000)")
    parser.add_argument("years", type=int, help="Term in years (e.g., 30)")
    parser.add_argument(
        "--rate",
        type=float,
        default=0.0,
        help="Annual interest rate in percent (e.g., 6.5). Default: 0 (no interest)",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Print the month-by-month amortization schedule",
    )
    parser.add_argument(
        "--inflation",
        type=float,
        default=0.0,
        help=(
            "Annual inflation rate in percent (e.g., 3.5). Discounts to present value "
            "using continuous compounding. Default: 0 (no discounting)"
        ),
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = _parse_args(argv)
    pmt = monthly_payment(args.loan, args.years, args.rate)
    has_infl = _inflation_enabled(args.inflation)

    if args.schedule:
        print(f"Monthly payment: {pmt:.2f}\n")
        print(_schedule_header(has_infl))
        total_npv = 0.0
        for row in amortization_schedule(args.loan, args.years, args.rate, args.inflation):
            if has_infl:
                total_npv += row["payment_real"]
            print(_format_row(row, has_infl))
            if row['month'] % 12 == 0:
                print("-" * 100)
        if has_infl:
            print(
                f"\nPresent value of all payments at {args.inflation:.2f}% inflation: {total_npv:.2f}")
    else:
        if has_infl:
            total_npv = 0.0
            for row in amortization_schedule(args.loan, args.years, args.rate, args.inflation):
                total_npv += row["payment_real"]
            print(f"Monthly payment: {pmt:.2f}")
            print(
                f"Present value of all payments at {args.inflation:.2f}% inflation: {total_npv:.2f}")
        else:
            print(f"Monthly payment: {pmt:.2f}")


if __name__ == "__main__":
    main()
