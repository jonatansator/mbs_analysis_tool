import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Step 1: PSA prepayment speed
def psa_prepayment_speed(month, psa_factor): # Monthly prepayment rate
    psa_multiplier = psa_factor / 100
    if month <= 30:
        cpr = 0.002 * (month / 30) * psa_multiplier
    else:
        cpr = 0.06 * psa_multiplier
    cpr = min(max(cpr, 0.0), 1.0)
    smm = 1 - (1 - cpr) ** (1 / 12)
    return smm

# Step 2: MBS cash flows
def mbs_cash_flows(principal, coupon_rate, term_months, psa_factor, discount_rate): # Generate cash flows
    monthly_rate = coupon_rate / 12
    balance = principal
    cash_flows = []
    factor = (1 + monthly_rate) ** term_months if monthly_rate > 0 else 1
    monthly_payment = principal / term_months if monthly_rate <= 0 else principal * monthly_rate * factor / (factor - 1)
    
    for month in range(1, term_months + 1):
        if balance <= 0:
            cash_flows.append(0)
            continue
        smm = psa_prepayment_speed(month, psa_factor)
        interest = balance * monthly_rate
        scheduled_principal = float(min(monthly_payment - interest, balance))
        prepayment = float(balance * smm)
        total_principal = float(min(scheduled_principal + prepayment, balance))
        cash_flows.append(interest + total_principal)
        balance -= total_principal
    
    return np.array(cash_flows)

# Step 3: Calculate WAL
def calculate_wal(cash_flows): # Weighted average life
    months = np.arange(1, len(cash_flows) + 1)
    return np.sum(cash_flows * months) / np.sum(cash_flows)

# Step 4: Price MBS
def price_mbs(cash_flows, discount_rate): # Discounted cash flow price
    discount_factors = np.array([(1 + discount_rate / 12) ** (-t) for t in range(1, len(cash_flows) + 1)])
    return np.sum(cash_flows * discount_factors)

# Step 5: Update GUI results
def update_results(): # Compute and plot results
    try:
        principal = float(e1.get())
        coupon_rate = float(e2.get()) / 100
        term_years = float(e3.get())
        psa_factor = float(e4.get())
        discount_rate = float(e5.get()) / 100

        if principal <= 0 or coupon_rate < 0 or term_years <= 0 or psa_factor < 0 or discount_rate < 0:
            raise ValueError("Inputs must be positive (discount rate can be zero)")

        term_months = int(term_years * 12)
        cash_flows = mbs_cash_flows(principal, coupon_rate, term_months, psa_factor, discount_rate)
        wal = calculate_wal(cash_flows)
        mbs_price = price_mbs(cash_flows, discount_rate)

        lbl_wal.config(text=f"WAL: {wal:.2f} months")
        lbl_price.config(text=f"MBS Price: ${mbs_price:.2f}")

        ax.clear()
        months = np.arange(1, term_months + 1)
        ax.fill_between(months, cash_flows, color='#FF6B6B', alpha=0.6, label=f'PSA {psa_factor:.0f}% Cash Flows')
        ax.axvline(wal, color='#4ECDC4', ls='--', lw=2, label=f'WAL = {wal:.1f} mo')
        ax.set_xlabel('Month', fontsize=12, color='white')
        ax.set_ylabel('Cash Flow ($)', fontsize=12, color='white')
        ax.set_title(f'MBS Cash Flows\nPrincipal=${principal:,.0f}, Coupon={coupon_rate*100:.1f}%', 
                     fontsize=12, color='white', pad=10)
        ax.set_facecolor('#2B2B2B')
        fig.set_facecolor('#1E1E1E')
        ax.grid(True, ls='--', color='#555555', alpha=0.3)
        ax.legend(loc='upper right', facecolor='#333333', edgecolor='white', labelcolor='white', fontsize=10)
        ax.tick_params(colors='white', labelsize=8)
        canv.draw()

    except ValueError as err:
        messagebox.showerror("Error", str(err))

# Step 6: Set up GUI
root = tk.Tk() # Initialize window
root.title("MBS Prepayment Model")
root.configure(bg='#1E1E1E')

frm = ttk.Frame(root, padding=10)
frm.pack()
frm.configure(style='Dark.TFrame')

fig, ax = plt.subplots(figsize=(7, 5))
canv = FigureCanvasTkAgg(fig, master=frm)
canv.get_tk_widget().pack(side=tk.LEFT)

pf = ttk.Frame(frm)
pf.pack(side=tk.RIGHT, padx=10)
pf.configure(style='Dark.TFrame')

style = ttk.Style()
style.theme_use('default')
style.configure('Dark.TFrame', background='#1E1E1E')
style.configure('Dark.TLabel', background='#1E1E1E', foreground='white')
style.configure('TButton', background='#333333', foreground='white')
style.configure('TEntry', fieldbackground='#333333', foreground='white')

ttk.Label(pf, text="Principal ($):", style='Dark.TLabel').pack(pady=3)
e1 = ttk.Entry(pf); e1.pack(pady=3); e1.insert(0, "1000000")
ttk.Label(pf, text="Coupon Rate (%):", style='Dark.TLabel').pack(pady=3)
e2 = ttk.Entry(pf); e2.pack(pady=3); e2.insert(0, "5.0")
ttk.Label(pf, text="Term (Years):", style='Dark.TLabel').pack(pady=3)
e3 = ttk.Entry(pf); e3.pack(pady=3); e3.insert(0, "30")
ttk.Label(pf, text="PSA Factor (%):", style='Dark.TLabel').pack(pady=3)
e4 = ttk.Entry(pf); e4.pack(pady=3); e4.insert(0, "100")
ttk.Label(pf, text="Discount Rate (%):", style='Dark.TLabel').pack(pady=3)
e5 = ttk.Entry(pf); e5.pack(pady=3); e5.insert(0, "4.0")

ttk.Button(pf, text="Calculate", command=update_results).pack(pady=10)

lbl_wal = ttk.Label(pf, text="WAL: ", style='Dark.TLabel'); lbl_wal.pack(pady=2)
lbl_price = ttk.Label(pf, text="MBS Price: ", style='Dark.TLabel'); lbl_price.pack(pady=2)

# Step 7: Run GUI
update_results() # Initial calculation
root.mainloop() # Start GUI loop
