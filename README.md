# mortgage

Mortgage calculator that also shows what the payments are worth in today's money.

A fixed monthly payment gets cheaper in real terms every year, because inflation
erodes it. With `--inflation`, each payment is discounted back to today at the
annual inflation rate you give, and the script prints the present value of all
payments: what the whole loan costs you in today's money.

## Usage

Needs Python 3.9 or newer, no dependencies.

    $ python mortgage.py 300_000 30 --rate 5.5
    Monthly payment: 1_703.37

    $ python mortgage.py 300000 30 --rate 5.5 --inflation 3.5
    Monthly payment: 1_703.37
    Present value of all payments at 3.50% inflation: 381_934.10

    $ python mortgage.py 300000 30 --rate 5.5 --inflation 3.5 --schedule

The last form prints the month-by-month schedule: payment, interest, principal and
balance, plus the discount factor and the same amounts in today's money.

## Arguments

    python mortgage.py LOAN YEARS [--rate R] [--inflation I] [--schedule]

| Argument | Meaning |
|---|---|
| `LOAN` (1st) | The amount borrowed, in any currency. `300000` and `300_000` both work. |
| `YEARS` (2nd) | The term of the loan in whole years. Payments are monthly, so 30 means 360 payments. |
| `--rate R` | Annual interest rate in percent, fixed for the whole term. Default 0. |
| `--inflation I` | Annual inflation rate in percent. Turns on the today's-money figures. Default 0 (off). |
| `--schedule` | Print the month-by-month table. |

## Test

    python test_mortgage.py
