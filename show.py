import tkinter as tk
from tkinter import ttk, messagebox
import math

def crf(i, n):
    """Capital Recovery Factor (A/P factor)"""
    return i * (1 + i)**n / ((1 + i)**n - 1)

class ReplacementAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Replacement Analysis Tool")
        self.root.geometry("1000x800")
        
        # Data storage
        self.assets = {
            'defender': {'years': 0, 'data': {}, 'aec': []},
            'challenger': {'years': 0, 'data': {}, 'aec': []}
        }
        
        # GUI components
        self.create_input_interface()
        self.create_results_interface()
        
        # Best combination tracking
        self.best_combination = None
        self.min_pw = float('inf')

    def create_input_interface(self):
        """Create input controls"""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=20)

        # Defender controls
        ttk.Label(control_frame, text="Defender Years:").grid(row=0, column=0)
        self.def_years = ttk.Entry(control_frame, width=5)
        self.def_years.grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Create Defender Table", 
                 command=lambda: self.create_asset_table('defender')).grid(row=0, column=2, padx=10)

        # Challenger controls
        ttk.Label(control_frame, text="Challenger Years:").grid(row=0, column=3)
        self.chal_years = ttk.Entry(control_frame, width=5)
        self.chal_years.grid(row=0, column=4, padx=5)
        ttk.Button(control_frame, text="Create Challenger Table",
                 command=lambda: self.create_asset_table('challenger')).grid(row=0, column=5, padx=10)

        # Analysis controls
        ttk.Label(control_frame, text="Service Life:").grid(row=1, column=0, pady=10)
        self.service_life = ttk.Entry(control_frame, width=5)
        self.service_life.grid(row=1, column=1)
        
        ttk.Label(control_frame, text="Interest Rate (%):").grid(row=1, column=3)
        self.rate = ttk.Entry(control_frame, width=5)
        self.rate.grid(row=1, column=4)
        
        ttk.Button(control_frame, text="Calculate Optimal", command=self.analyze).grid(row=1, column=5)

    def create_asset_table(self, asset_type):
        """Create input table for specified asset"""
        try:
            years = int(self.def_years.get() if asset_type == 'defender' else self.chal_years.get())
            if years < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid number of years")
            return

        # Clear previous data
        self.assets[asset_type]['data'] = {}
        frame = ttk.Frame(self.root)
        frame.pack(pady=10)

        # Table headers
        headers = ["Year", "Initial Cost", "Salvage Value", "Operating Cost"]
        for col, header in enumerate(headers):
            ttk.Label(frame, text=header, relief="solid", padding=5, 
                    font=('Helvetica', 10, 'bold')).grid(row=0, column=col, sticky="nsew")

        # Create entries
        for year in range(years + 1):
            ttk.Label(frame, text=f"Year {year}", relief="solid", padding=5).grid(row=year+1, column=0)
            
            entries = {}
            if year == 0:
                entries["initial"] = ttk.Entry(frame)
                entries["initial"].grid(row=year+1, column=1, padx=2, pady=2)
                
                entries["salvage"] = ttk.Entry(frame)
                entries["salvage"].grid(row=year+1, column=2, padx=2, pady=2)
                
                ttk.Label(frame, text="N/A").grid(row=year+1, column=3)
            else:
                ttk.Label(frame, text="N/A").grid(row=year+1, column=1)
                
                entries["salvage"] = ttk.Entry(frame)
                entries["salvage"].grid(row=year+1, column=2, padx=2, pady=2)
                
                entries["operating"] = ttk.Entry(frame)
                entries["operating"].grid(row=year+1, column=3, padx=2, pady=2)
            
            self.assets[asset_type]['data'][year] = entries

        self.assets[asset_type]['years'] = years

    def calculate_aec(self, asset_type):
        """Calculate AEC for given asset type"""
        data = self.assets[asset_type]['data']
        years = self.assets[asset_type]['years']
        i = float(self.rate.get()) / 100
        aec_values = []

        for n in range(1, years + 1):
            # Capital Recovery Component
            initial = float(data[0]["initial"].get())
            salvage_0 = float(data[0]["salvage"].get())
            salvage_n = float(data[n]["salvage"].get())
            
            crf_val = crf(i, n)
            af_val = crf_val / ((1 + i)**n)
            aec_cr = (initial + salvage_0) * crf_val - salvage_n * af_val

            # Operating Cost Component
            pv_oc = sum(float(data[y]["operating"].get()) / ((1 + i)**y) for y in range(1, n+1))
            aec_oc = pv_oc * crf_val

            aec_values.append({
                'years': n,
                'cr': aec_cr,
                'oc': aec_oc,
                'total': aec_cr + aec_oc
            })
        
        self.assets[asset_type]['aec'] = aec_values

    def analyze(self):
        """Main analysis function"""
        try:
            # Validate inputs
            service_life = int(self.service_life.get())
            if service_life < 1:
                raise ValueError
            
            # Calculate AEC for both assets
            for asset_type in ['defender', 'challenger']:
                self.calculate_aec(asset_type)
            
            # Find optimal combination
            self.find_optimal_combination(service_life)
            
            # Show results
            self.show_results()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid input values")
            return

    def find_optimal_combination(self, service_life):
        """Find best combination of assets"""
        self.min_pw = float('inf')
        self.best_combination = (None, None)

        # Check all defender-challenger combinations
        for d in self.assets['defender']['aec']:
            remaining = service_life - d['years']
            if remaining < 0:
                continue
                
            for c in self.assets['challenger']['aec']:
                if c['years'] == remaining:
                    pw = self.calculate_pw([d], [c])
                    if pw < self.min_pw:
                        self.min_pw = pw
                        self.best_combination = (d, c)

        # Check challenger-only option
        for c in self.assets['challenger']['aec']:
            if c['years'] == service_life:
                pw = self.calculate_pw([], [c])
                if pw < self.min_pw:
                    self.min_pw = pw
                    self.best_combination = (None, c)

    def calculate_pw(self, defender_components, challenger_components):
        """Calculate present worth of a combination"""
        pw = 0
        cumulative = 0
        i = float(self.rate.get()) / 100
        
        for comp in defender_components:
            pw += comp['total'] * ((1 + i)**comp['years'] - 1) / (i * (1 + i)**cumulative)
            cumulative += comp['years']
            
        for comp in challenger_components:
            pw += comp['total'] * ((1 + i)**comp['years'] - 1) / (i * (1 + i)**cumulative)
            cumulative += comp['years']
            
        return pw

    def create_results_interface(self):
        """Create results display area"""
        self.results_frame = ttk.Frame(self.root)
        self.results_frame.pack(pady=20, fill=tk.BOTH, expand=True)

    def show_results(self):
        """Display results in table format"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Create results tables
        self.create_aec_table('defender')
        self.create_aec_table('challenger')
        self.create_combination_table()

    def create_aec_table(self, asset_type):
        """Create AEC table for specified asset"""
        frame = ttk.Frame(self.results_frame)
        frame.pack(pady=10, padx=20, fill=tk.X)

        # Title
        title_label = ttk.Label(frame, text=f"{asset_type.capitalize()} AEC Analysis", 
                              font=('Helvetica', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=5)

        # Table headers
        headers = ["Years", "CR Component", "OC Component", "Total AEC"]
        for col, header in enumerate(headers):
            ttk.Label(frame, text=header, relief="solid", padding=5,
                    font=('Helvetica', 10, 'bold')).grid(row=1, column=col, sticky="nsew")

        # Table rows
        for row, aec in enumerate(self.assets[asset_type]['aec'], start=2):
            ttk.Label(frame, text=aec['years']).grid(row=row, column=0)
            ttk.Label(frame, text=f"${aec['cr']:,.2f}").grid(row=row, column=1)
            ttk.Label(frame, text=f"${aec['oc']:,.2f}").grid(row=row, column=2)
            ttk.Label(frame, text=f"${aec['total']:,.2f}").grid(row=row, column=3)

    def create_combination_table(self):
        """Display optimal combination results"""
        frame = ttk.Frame(self.results_frame)
        frame.pack(pady=20, padx=20, fill=tk.X)

        # Title
        ttk.Label(frame, text="Optimal Combination", 
                font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=3, pady=5)

        # Table headers
        headers = ["Component", "Years", "AEC Value"]
        for col, header in enumerate(headers):
            ttk.Label(frame, text=header, relief="solid", padding=5,
                    font=('Helvetica', 10, 'bold')).grid(row=1, column=col, sticky="nsew")

        # Table rows
        row = 2
        if self.best_combination[0]:
            ttk.Label(frame, text="Defender").grid(row=row, column=0)
            ttk.Label(frame, text=self.best_combination[0]['years']).grid(row=row, column=1)
            ttk.Label(frame, text=f"${self.best_combination[0]['total']:,.2f}").grid(row=row, column=2)
            row += 1

        if self.best_combination[1]:
            ttk.Label(frame, text="Challenger").grid(row=row, column=0)
            ttk.Label(frame, text=self.best_combination[1]['years']).grid(row=row, column=1)
            ttk.Label(frame, text=f"${self.best_combination[1]['total']:,.2f}").grid(row=row, column=2)
            row += 1

        # Present Worth
        ttk.Label(frame, text="Total Present Worth", font=('Helvetica', 10, 'bold')).grid(row=row, column=0)
        ttk.Label(frame, text=f"${self.min_pw:,.2f}", font=('Helvetica', 10, 'bold')).grid(row=row, column=1, columnspan=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = ReplacementAnalyzer(root)
    root.mainloop()