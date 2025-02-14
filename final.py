import tkinter as tk
from tkinter import ttk, messagebox
import math

def crf(i, n):
    """Capital Recovery Factor for n years at interest rate i (A/P factor)."""
    return i * (1 + i)**n / ((1 + i)**n - 1)

# Data storage dictionaries
data = {
    'defender': {},
    'challenger': {}
}
entries = {
    'defender': {},
    'challenger': {}
}

# Global configuration
set1 = []       # Defender years
values1 = []    # Defender AEC values
set2 = []       # Challenger years
values2 = []    # Challenger AEC values
size1 = 0       # Defender size
size2 = 0       # Challenger size
total_years = 0 # Service life
i_rate = 0.0    # Interest rate
min_pw = float("inf")
best_defender = None
best_challenger = None

def create_table(years_entry, parent_frame, asset_type):
    try:
        num_years = int(years_entry.get())
        if num_years < 1:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number of years (≥1)")
        return

    # Clear previous widgets
    for widget in parent_frame.winfo_children():
        if not isinstance(widget, ttk.Frame):
            widget.destroy()

    table_frame = ttk.Frame(parent_frame)
    table_frame.pack(pady=10)

    # Create headers
    headers = ["Year", "Initial Investment", "Salvage Value", "Operating Cost"]
    for col, header in enumerate(headers):
        ttk.Label(table_frame, text=header, font=('Helvetica', 10, 'bold'), 
                 borderwidth=1, relief="solid", padding=5).grid(row=0, column=col, sticky="nsew")

    # Create entries
    entries[asset_type] = {}
    for year in range(num_years + 1):
        row = year + 1
        ttk.Label(table_frame, text=f"Year {year}", relief="solid", padding=5).grid(row=row, column=0, sticky="nsew")
        
        entries[asset_type][year] = {}
        if year == 0:
            # Initial investment and salvage
            entries[asset_type][year]["initial"] = ttk.Entry(table_frame)
            entries[asset_type][year]["initial"].grid(row=row, column=1, padx=2, pady=2, sticky="nsew")
            
            entries[asset_type][year]["salvage"] = ttk.Entry(table_frame)
            entries[asset_type][year]["salvage"].grid(row=row, column=2, padx=2, pady=2, sticky="nsew")
            
            ttk.Label(table_frame, text="N/A").grid(row=row, column=3, sticky="nsew")
        else:
            # Salvage and operating costs
            ttk.Label(table_frame, text="N/A").grid(row=row, column=1, sticky="nsew")
            
            entries[asset_type][year]["salvage"] = ttk.Entry(table_frame)
            entries[asset_type][year]["salvage"].grid(row=row, column=2, padx=2, pady=2, sticky="nsew")
            
            entries[asset_type][year]["operating"] = ttk.Entry(table_frame)
            entries[asset_type][year]["operating"].grid(row=row, column=3, padx=2, pady=2, sticky="nsew")

    ttk.Button(parent_frame, text="Submit Data", 
              command=lambda: submit_data(num_years, asset_type)).pack(pady=10)

def submit_data(num_years, asset_type):
    try:
        # Process Year 0 data
        initial = float(entries[asset_type][0]["initial"].get())
        salvage = float(entries[asset_type][0]["salvage"].get())
        data[asset_type][0] = {"Initial": initial, "Salvage": salvage, "Operating": None}
        
        # Process subsequent years
        for year in range(1, num_years + 1):
            salvage = float(entries[asset_type][year]["salvage"].get())
            operating = float(entries[asset_type][year]["operating"].get())
            data[asset_type][year] = {"Salvage": salvage, "Operating": operating}
            
        # Update global configuration
        if asset_type == 'defender':
            global size1, set1, values1
            size1 = num_years
            set1 = list(range(1, size1 + 1))
            values1 = [0.0] * size1  # Initialize with correct size
        else:
            global size2, set2, values2
            size2 = num_years
            set2 = list(range(1, size2 + 1))
            values2 = [0.0] * size2
            
        messagebox.showinfo("Success", f"{asset_type.capitalize()} data saved!")
        
    except ValueError:
        messagebox.showerror("Error", "Invalid numeric input")
        return

def calculate_aec():
    global values1, values2, i_rate
    
    try:
        i_rate = float(rate_entry.get()) / 100.0
        if i_rate <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Invalid interest rate")
        return

    # Calculate AEC for both assets
    for asset_type in ['defender', 'challenger']:
        if not data.get(asset_type):
            messagebox.showerror("Error", f"Missing {asset_type} data")
            return
            
        asset_data = data[asset_type]
        num_years = max(asset_data.keys())
        values = []
        
        for n in range(1, num_years + 1):
            I = asset_data[0]["Initial"] + asset_data[0]["Salvage"]
            S_n = asset_data[n]["Salvage"]
            
            crf_val = crf(i_rate, n)
            af_val = crf_val / ((1 + i_rate)**n)
            aec_cr = I * crf_val - S_n * af_val
            
            pv_oc = sum(asset_data[k]["Operating"] / ((1 + i_rate)**k) for k in range(1, n+1))
            aec_oc = pv_oc * crf_val
            
            values.append(aec_cr + aec_oc)
            
        if asset_type == 'defender':
            values1 = values
        else:
            values2 = values
            
    find_optimal_combination()

# Combination logic
def find_optimal_combination():
    global min_pw, best_defender, best_challenger, total_years
    
    try:
        total_years = int(service_entry.get())
        if total_years < 1:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Invalid service life")
        return
    
    min_pw = float("inf")
    best_defender = None
    best_challenger = None
    
    # Check defender combinations
    for d_idx in range(size1):
        defender_years = set1[d_idx]
        remaining = total_years - defender_years
        if remaining < 0:
            continue
            
        # Find challenger combinations
        for c_idx in range(size2):
            if set2[c_idx] == remaining:
                current_pw = calculate_pw([d_idx], [c_idx])
                if current_pw < min_pw:
                    min_pw = current_pw
                    best_defender = [d_idx]
                    best_challenger = [c_idx]
    
    # Check challenger-only combinations
    for c_idx in range(size2):
        if set2[c_idx] == total_years:
            current_pw = calculate_pw(None, [c_idx])
            if current_pw < min_pw:
                min_pw = current_pw
                best_defender = None
                best_challenger = [c_idx]
                
    display_optimal()

def calculate_pw(def_indices, chal_indices):
    pw = 0.0
    cumulative = 0
    
    if def_indices:
        for idx in def_indices:
            if idx >= len(set1) or idx >= len(values1):
                continue
            pw += values1[idx] * P_A(i_rate, set1[idx]) * P_F(i_rate, cumulative)
            cumulative += set1[idx]
            
    if chal_indices:
        for idx in chal_indices:
            if idx >= len(set2) or idx >= len(values2):
                continue
            pw += values2[idx] * P_A(i_rate, set2[idx]) * P_F(i_rate, cumulative)
            cumulative += set2[idx]
            
    return pw

def P_F(i, n):
    return 1 / (1 + i)**n

def P_A(i, n):
    if i == 0:
        return n
    return (1 - (1 + i)**-n) / i

def display_optimal():
    result_win = tk.Toplevel()
    result_win.title("Optimal Combination")
    
    if best_defender is not None:
        ttk.Label(result_win, text="Defender Components:", font=('Helvetica', 10, 'bold')).pack()
        for idx in best_defender:
            if idx < len(set1) and idx < len(values1):
                ttk.Label(result_win, text=f"Year {set1[idx]}: ${values1[idx]:.2f}").pack()
                
    if best_challenger is not None:
        ttk.Label(result_win, text="Challenger Components:", font=('Helvetica', 10, 'bold')).pack()
        for idx in best_challenger:
            if idx < len(set2) and idx < len(values2):
                ttk.Label(result_win, text=f"Year {set2[idx]}: ${values2[idx]:.2f}").pack()
                
    ttk.Label(result_win, text=f"Minimum Present Worth: ${min_pw:.2f}", font=('Helvetica', 10, 'bold')).pack()

# GUI Setup
root = tk.Tk()
root.title("Replacement Analysis Tool")
root.geometry("800x600")

notebook = ttk.Notebook(root)
defender_frame = ttk.Frame(notebook)
challenger_frame = ttk.Frame(notebook)
notebook.add(defender_frame, text="Defender")
notebook.add(challenger_frame, text="Challenger")
notebook.pack(expand=True, fill='both')

# Defender Tab
defender_controls = ttk.Frame(defender_frame)
defender_controls.pack(pady=10)
ttk.Label(defender_controls, text="Defender Years:").pack(side=tk.LEFT)
defender_years_entry = ttk.Entry(defender_controls, width=5)
defender_years_entry.pack(side=tk.LEFT, padx=5)
ttk.Button(defender_controls, text="Create Table", 
          command=lambda: create_table(defender_years_entry, defender_frame, 'defender')).pack(side=tk.LEFT)

# Challenger Tab
challenger_controls = ttk.Frame(challenger_frame)
challenger_controls.pack(pady=10)
ttk.Label(challenger_controls, text="Challenger Years:").pack(side=tk.LEFT)
challenger_years_entry = ttk.Entry(challenger_controls, width=5)
challenger_years_entry.pack(side=tk.LEFT, padx=5)
ttk.Button(challenger_controls, text="Create Table", 
          command=lambda: create_table(challenger_years_entry, challenger_frame, 'challenger')).pack(side=tk.LEFT)

# Control Panel
control_frame = ttk.Frame(root)
control_frame.pack(pady=20)

ttk.Label(control_frame, text="Service Life (years):").grid(row=0, column=0, padx=5)
service_entry = ttk.Entry(control_frame, width=8)
service_entry.grid(row=0, column=1, padx=5)

ttk.Label(control_frame, text="Interest Rate (%):").grid(row=0, column=2, padx=5)
rate_entry = ttk.Entry(control_frame, width=8)
rate_entry.grid(row=0, column=3, padx=5)

ttk.Button(control_frame, text="Calculate Optimal", command=calculate_aec).grid(row=0, column=4, padx=10)

root.mainloop()