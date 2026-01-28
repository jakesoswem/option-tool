# gui.py
"""
Swem Team Trading Suite: GUI Frontend
Tkinter interface for the Strategy Auditor.
Depends on audit.py for calculations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict
from audit import audit_strategy, LegInput, AuditResult


class StrategyAuditorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Swem Team Strategy Auditor")
        self.root.geometry("700x600")
        self.root.configure(bg="#f5f6fa")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background="#f5f6fa")
        
        self.leg_entries: List[Dict] = []
        
        self._create_ui()
        self._add_default_legs()
    
    def _create_ui(self) -> None:
        # Header
        ttk.Label(self.root, text="Swem Team Trading Suite", style="Header.TLabel").pack(pady=10)
        ttk.Label(self.root, text="Unified Strategy Auditor", font=("Helvetica", 10), 
                 background="#f5f6fa", foreground="#666").pack()
        
        # Presets
        preset_frame = tk.Frame(self.root, bg="#f5f6fa")
        preset_frame.pack(pady=15)
        
        ttk.Button(preset_frame, text="Iron Condor", command=self._preset_iron_condor).pack(side=tk.LEFT, padx=5)
        ttk.Button(preset_frame, text="Bull Put", command=self._preset_bull_put).pack(side=tk.LEFT, padx=5)
        ttk.Button(preset_frame, text="Bear Call", command=self._preset_bear_call).pack(side=tk.LEFT, padx=5)
        
        # Legs Container
        self.legs_container = tk.LabelFrame(
            self.root, text="Option Legs", bg="#ffffff", 
            padx=10, pady=10, font=("Helvetica", 10, "bold")
        )
        self.legs_container.pack(padx=20, pady=10, fill=tk.X)
        
        # Headers
        for i, text in enumerate(["Type", "Action", "Delta (abs)", ""]):
            ttk.Label(self.legs_container, text=text, font=("Helvetica", 9, "bold")).grid(row=0, column=i, padx=5, pady=5)
        
        # Controls
        ctrl_frame = tk.Frame(self.root, bg="#f5f6fa")
        ctrl_frame.pack(pady=10)
        
        ttk.Button(ctrl_frame, text="+ Add Leg", command=self._add_leg).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text="Clear All", command=self._clear_legs).pack(side=tk.LEFT, padx=5)
        
        # Calculate Button
        calc_btn = tk.Button(
            self.root, text="AUDIT STRATEGY", command=self._calculate,
            bg="#2ecc71", fg="white", font=("Helvetica", 12, "bold"),
            padx=30, pady=10, relief=tk.FLAT, cursor="hand2"
        )
        calc_btn.pack(pady=15)
        calc_btn.bind("<Enter>", lambda e: calc_btn.config(bg="#27ae60"))
        calc_btn.bind("<Leave>", lambda e: calc_btn.config(bg="#2ecc71"))
        
        # Results
        self.result_frame = tk.LabelFrame(
            self.root, text="Audit Results", bg="#ffffff",
            padx=15, pady=15, font=("Helvetica", 10, "bold")
        )
        self.result_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        self.result_text = tk.Text(
            self.result_frame, height=8, font=("Courier", 11),
            bg="#f8f9fa", relief=tk.FLAT, padx=10, pady=10
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self._update_result_display("Ready to analyze...")
        
        # Status Bar
        self.status = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _add_default_legs(self) -> None:
        """Initialize with 2 legs (minimum for a spread)"""
        self._add_leg("call", "sell", 0.15)
        self._add_leg("call", "buy", 0.05)
    
    def _add_leg(self, preset_type: str = "call", preset_action: str = "sell", preset_delta: float = 0.15) -> None:
        """Add a new leg row to the form"""
        row = len(self.leg_entries) + 1
        
        type_var = tk.StringVar(value=preset_type)
        ttk.Combobox(
            self.legs_container, textvariable=type_var,
            values=["call", "put"], width=10, state="readonly"
        ).grid(row=row, column=0, padx=5, pady=3)
        
        action_var = tk.StringVar(value=preset_action)
        ttk.Combobox(
            self.legs_container, textvariable=action_var,
            values=["buy", "sell"], width=10, state="readonly"
        ).grid(row=row, column=1, padx=5, pady=3)
        
        delta_var = tk.StringVar(value=str(preset_delta))
        delta_entry = ttk.Entry(self.legs_container, textvariable=delta_var, width=12)
        delta_entry.grid(row=row, column=2, padx=5, pady=3)
        
        remove_btn = tk.Button(
            self.legs_container, text="×",
            command=lambda: self._remove_leg(row-1),
            bg="#e74c3c", fg="white", width=3, relief=tk.FLAT, cursor="hand2"
        )
        remove_btn.grid(row=row, column=3, padx=5, pady=3)
        
        self.leg_entries.append({
            'type': type_var,
            'action': action_var,
            'delta': delta_var,
            'widgets': [w for w in self.legs_container.grid_slaves() if int(w.grid_info()['row']) == row]
        })
    
    def _remove_leg(self, index: int) -> None:
        """Remove a leg row and reindex"""
        if len(self.leg_entries) <= 1:
            messagebox.showwarning("Warning", "Strategy must have at least one leg")
            return
        
        # Destroy widgets
        for widget in self.leg_entries[index]['widgets']:
            widget.destroy()
        
        self.leg_entries.pop(index)
        self._reindex_rows()
    
    def _reindex_rows(self) -> None:
        """Reindex grid rows after removal"""
        for i, entry in enumerate(self.leg_entries):
            for widget in entry['widgets']:
                widget.grid(row=i+1)
    
    def _clear_legs(self) -> None:
        """Remove all legs and reset to default"""
        for entry in self.leg_entries:
            for widget in entry['widgets']:
                widget.destroy()
        self.leg_entries.clear()
        self._add_default_legs()
    
    def _preset_iron_condor(self) -> None:
        """Load Iron Condor preset (4 legs)"""
        self._clear_legs()
        presets = [
            ('call', 'sell', 0.15),
            ('call', 'buy', 0.05),
            ('put', 'sell', 0.15),
            ('put', 'buy', 0.05)
        ]
        # Clear and repopulate with exact count
        for entry in self.leg_entries[:]:
            for widget in entry['widgets']:
                widget.destroy()
        self.leg_entries.clear()
        
        for t, a, d in presets:
            self._add_leg(t, a, d)
    
    def _preset_bull_put(self) -> None:
        """Load Bull Put Spread preset"""
        self._clear_legs()
        self.leg_entries[0]['type'].set('put')
        self.leg_entries[0]['action'].set('sell')
        self.leg_entries[0]['delta'].set('0.20')
        
        self.leg_entries[1]['type'].set('put')
        self.leg_entries[1]['action'].set('buy')
        self.leg_entries[1]['delta'].set('0.10')
    
    def _preset_bear_call(self) -> None:
        """Load Bear Call Spread preset"""
        self._clear_legs()
        self.leg_entries[0]['type'].set('call')
        self.leg_entries[0]['action'].set('sell')
        self.leg_entries[0]['delta'].set('0.20')
        
        self.leg_entries[1]['type'].set('call')
        self.leg_entries[1]['action'].set('buy')
        self.leg_entries[1]['delta'].set('0.10')
    
    def _calculate(self) -> None:
        """Gather inputs and call audit logic"""
        legs: List[LegInput] = []
        errors = []
        
        for i, entry in enumerate(self.leg_entries):
            try:
                delta_val = float(entry['delta'].get())
                if not 0 <= delta_val <= 1:
                    errors.append(f"Leg {i+1}: Delta must be between 0.0 and 1.0")
                    continue
                
                legs.append({
                    'type': entry['type'].get(),
                    'action': entry['action'].get(),
                    'delta': delta_val
                })
            except ValueError:
                errors.append(f"Leg {i+1}: Invalid delta value '{entry['delta'].get()}'")
        
        if errors:
            messagebox.showerror("Input Error", "\n".join(errors))
            return
        
        if len(legs) < 2:
            messagebox.showwarning("Warning", "A complete strategy typically requires at least 2 legs")
            return
        
        try:
            results = audit_strategy(legs)
            self._display_results(results)
            self.status.config(
                text=f"Audit: {results['Strategy']} | Bias: {results['Directional_Bias']} | "
                     f"Δ: {results['Net_Delta']} | POP: {results['Prob_of_Success']}"
            )
        except Exception as e:
            messagebox.showerror("Calculation Error", str(e))
    
    def _display_results(self, results: AuditResult) -> None:
        """Format and display audit results"""
        display = (
            "╔══════════════════════════════════╗\n"
            "║     SWEM TEAM TRADE AUDIT        ║\n"
            "╠══════════════════════════════════╣\n"
            f"║ Strategy         : {results['Strategy']:<16}║\n"
            f"║ Directional Bias : {results['Directional_Bias']:<16}║\n"
            f"║ Net Delta        : {results['Net_Delta']:<16.3f}║\n"
            f"║ Prob of Success  : {results['Prob_of_Success']:<16}║\n"
            "╚══════════════════════════════════╝"
        )
        self._update_result_display(display)
    
    def _update_result_display(self, text: str) -> None:
        """Helper to update result text widget"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, text)
        self.result_text.config(state=tk.DISABLED)


def launch_gui() -> None:
    """Entry point for GUI application"""
    root = tk.Tk()
    app = StrategyAuditorGUI(root)
    root.mainloop()
