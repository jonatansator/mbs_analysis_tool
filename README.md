# MBS Analysis Tool

- This project calculates cash flows, weighted average life (WAL), and pricing for a Mortgage-Backed Security (MBS) using a PSA prepayment model.
- It features a GUI built with Tkinter for user input and visualizes cash flows using Matplotlib.

---

## Files
- `mbs_analysis.py`: Main script for calculating MBS metrics and running the GUI.
- `output.png`: Plot.

---

## Libraries Used
- `numpy`
- `matplotlib`
- `tkinter`
- `matplotlib.backends.backend_tkagg`

---

## Features
- **Input**: 
  - Principal amount (e.g., $1,000,000)
  - Coupon rate (e.g., 5.0%)
  - Term in years (e.g., 30 years)
  - PSA prepayment speed (e.g., 100%)
  - Discount rate (e.g., 4.0%)
- **Output**: 
  - Weighted Average Life (WAL) in months
  - MBS price in dollars
  - Dynamic plot of cash flows over time

---

## Methodology
- **Prepayment Speed**: Calculated using the PSA model with a ramp-up period (0.2% CPR per month for 30 months) and a steady state (6% CPR), adjusted by the PSA factor.
- **Cash Flows**: Generated based on principal, coupon rate, term, PSA factor, and discount rate.
- **WAL**: Computed as the sum of cash flows times their periods divided by total cash flows.
- **Price**: Discounted present value of cash flows using the specified discount rate.
