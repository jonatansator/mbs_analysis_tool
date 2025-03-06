import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# MBS Prepayment Model Functions
def psa_prepayment_speed(month, psa_factor):
    """Calculate monthly prepayment speed based on PSA model."""
    psa_multiplier = psa_factor / 100  # Convert percentage to multiplier (e.g., 100 -> 1.0)
    if month <= 30:
        cpr = 0.002 * (month / 30) * psa_multiplier  # Ramps to 6% at 100% PSA
    else:
        cpr = 0.06 * psa_multiplier  # Steady at 6% * multiplier after 30 months
    cpr = min(max(cpr, 0.0), 1.0)  # Cap CPR between 0 and 1
    smm = 1 - (1 - cpr) ** (1 / 12)
    return smm

def mbs_cash_flows(principal, coupon_rate, term_months, psa_factor, discount_rate):
    """Generate MBS cash flows with prepayments."""
    monthly_rate = coupon_rate / 12
    balance = principal
    cash_flows = []
    
    # Calculate fixed monthly payment using a numerically stable formula
    if monthly_rate <= 0:  # Handle zero or negative rate
        monthly_payment = principal / term_months
    else:
        factor = (1 + monthly_rate) ** term_months
        monthly_payment = principal * monthly_rate * factor / (factor - 1)
    
    for month in range(1, term_months + 1):
        if balance <= 0:
            cash_flows.append(0)
            continue
        smm = psa_prepayment_speed(month, psa_factor)
        interest = balance * monthly_rate
        scheduled_principal = float(min(monthly_payment - interest, balance))
        prepayment = float(balance * smm)
        total_principal = float(min(scheduled_principal + prepayment, balance))
        cash_flow = interest + total_principal
        cash_flows.append(cash_flow)
        balance -= total_principal
    
    return np.array(cash_flows)

def calculate_wal(cash_flows):
    """Calculate Weighted Average Life (WAL)."""
    months = np.arange(1, len(cash_flows) + 1)
    return np.sum(cash_flows * months) / np.sum(cash_flows)

def price_mbs(cash_flows, discount_rate):
    """Price the MBS by discounting cash flows."""
    discount_factors = np.array([(1 + discount_rate / 12) ** (-t) for t in range(1, len(cash_flows) + 1)])
    return np.sum(cash_flows * discount_factors)

# GUI Logic
def update_results():
    try:
        principal = float(e1.get())
        coupon_rate = float(e2.get()) / 100  # Convert percentage to decimal
        term_years = float(e3.get())
        psa_factor = float(e4.get())  # Input as percentage (e.g., 100 for 100% PSA)
        discount_rate = float(e5.get()) / 100  # Convert percentage to decimal

        # Validate inputs
        if principal <= 0 or coupon_rate < 0 or term_years <= 0 or psa_factor < 0 or discount_rate < 0:
            raise ValueError("All inputs must be positive (except discount rate, which can be zero)")

        term_months = int(term_years * 12)
        cash_flows = mbs_cash_flows(principal, coupon_rate, term_months, psa_factor, discount_rate)
        wal = calculate_wal(cash_flows)
        mbs_price = price_mbs(cash_flows, discount_rate)

        # Update labels
        lbl_wal.config(text=f"WAL: {wal:.2f} months")
        lbl_price.config(text=f"MBS Price: ${mbs_price:.2f}")

        # Plot cash flows
        ax.clear()
        months = np.arange(1, term_months + 1)
        ax.plot(months, cash_flows, color='#FF6B6B', lw=2, label=f'PSA {psa_factor:.0f}% Cash Flows')
        ax.set_xlabel('Month', color='white')
        ax.set_ylabel('Cash Flow ($)', color='white')
        ax.set_title('MBS Cash Flows', color='white')
        ax.set_facecolor('#2B2B2B')
        fig.set_facecolor('#1E1E1E')
        ax.grid(True, ls='--', color='#555555', alpha=0.5)
        ax.legend(facecolor='#333333', edgecolor='white', labelcolor='white')
        ax.tick_params(colors='white')
        canv.draw()

    except ValueError as err:
        messagebox.showerror("Error", str(err))

# Set up GUI
root = tk.Tk()
root.title("MBS Prepayment Model")
root.configure(bg='#1E1E1E')

frm = ttk.Frame(root, padding=10)
frm.pack()
frm.configure(style='Dark.TFrame')

# Create plot
fig, ax = plt.subplots(figsize=(7, 5))
canv = FigureCanvasTkAgg(fig, master=frm)
canv.get_tk_widget().pack(side=tk.LEFT)

# Create input panel
pf = ttk.Frame(frm)
pf.pack(side=tk.RIGHT, padx=10)
pf.configure(style='Dark.TFrame')

# Dark theme style
style = ttk.Style()
style.theme_use('default')
style.configure('Dark.TFrame', background='#1E1E1E')
style.configure('Dark.TLabel', background='#1E1E1E', foreground='white')
style.configure('TButton', background='#333333', foreground='white')
style.configure('TEntry', fieldbackground='#333333', foreground='white')

# Input fields
ttk.Label(pf, text="Principal ($):", style='Dark.TLabel').pack(pady=3)
e1 = ttk.Entry(pf); e1.pack(pady=3); e1.insert(0, "1000000")  # Default $1M
ttk.Label(pf, text="Coupon Rate (%):", style='Dark.TLabel').pack(pady=3)
e2 = ttk.Entry(pf); e2.pack(pady=3); e2.insert(0, "5.0")  # Default 5%
ttk.Label(pf, text="Term (Years):", style='Dark.TLabel').pack(pady=3)
e3 = ttk.Entry(pf); e3.pack(pady=3); e3.insert(0, "30")  # Default 30 years
ttk.Label(pf, text="PSA Factor (%):", style='Dark.TLabel').pack(pady=3)
e4 = ttk.Entry(pf); e4.pack(pady=3); e4.insert(0, "100")  # Default 100% PSA
ttk.Label(pf, text="Discount Rate (%):", style='Dark.TLabel').pack(pady=3)
e5 = ttk.Entry(pf); e5.pack(pady=3); e5.insert(0, "4.0")  # Default 4%

# Run button
ttk.Button(pf, text="Calculate", command=update_results).pack(pady=10)

# Output labels
lbl_wal = ttk.Label(pf, text="WAL: ", style='Dark.TLabel'); lbl_wal.pack(pady=2)
lbl_price = ttk.Label(pf, text="MBS Price: ", style='Dark.TLabel'); lbl_price.pack(pady=2)

# Initial run and GUI loop
update_results()
root.mainloop()