"""Run with: python test_mortgage.py"""
from mortgage import amortization_schedule, monthly_payment

assert round(monthly_payment(300000, 30), 2) == 833.33
assert round(monthly_payment(300000, 30, 5.5), 2) == 1703.37

for loan, years, rate in [(300000, 30, 5.5), (45_000_000, 20, 6.79), (123456.78, 7, 0.1), (1000, 1, 0)]:
    rows = list(amortization_schedule(loan, years, rate))
    assert len(rows) == years * 12
    assert abs(rows[-1]["balance"]) < 0.005, rows[-1]
    assert abs(sum(r["principal"] for r in rows) - loan) < 0.005

# 3.5% inflation: a payment due in exactly one year is worth 1/1.035 of its face value
row12 = list(amortization_schedule(1000, 1, 5, 3.5))[11]
assert abs(row12["discount"] - 1 / 1.035) < 1e-12

print("ok")
