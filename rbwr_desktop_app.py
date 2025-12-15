# rbwr_desktop_app.py
import tkinter as tk
from tkinter import ttk, font
import random
import time
from threading import Thread

class RBWRReactor:
    """Reactor physics simulation"""
    def __init__(self):
        self.thermal_power = 0.0001  # %
        self.temperature = 31  # °C
        self.pressure = 0  # kPa
        self.feedwater_flow = 0  # kg/s
        self.turbine_speed = 0  # RPM
        self.generator_load = 0  # MW
        self.rods_position = 0.0  # %
        self.circulation_flow = 0  # %
        self.xenon_poisoning = 10.1  # %
        self.fuel_remaining = 98.0  # %
        self.is_scrammed = False
        self.is_auto = False
        
    def update(self):
        """Update reactor state based on physics"""
        if self.is_scrammed:
            # SCRAM mode: power drops, rods don't move to 0 instantly
            self.thermal_power *= 0.7
            self.temperature -= 5
            self.pressure *= 0.8
            self.turbine_speed *= 0.9
            self.generator_load = self.thermal_power * 12
        else:
            # Normal operation
            rod_effect = (100 - self.rods_position) / 100
            
            # Power calculation
            if self.is_auto:
                # Auto mode tries to maintain 95% power
                target_power = 95.0
                if self.thermal_power < target_power:
                    self.rods_position = max(0, self.rods_position - 0.5)
                else:
                    self.rods_position = min(100, self.rods_position + 0.5)
            
            power_change = rod_effect * random.uniform(0.95, 1.05)
            self.thermal_power = max(0.0001, min(120.0, self.thermal_power * power_change))
            
            # Other parameters
            self.temperature = 30 + (self.thermal_power * 3) + random.uniform(-2, 2)
            self.pressure = int(self.thermal_power * 60 + random.uniform(-100, 100))
            self.feedwater_flow = self.thermal_power * 4 + random.uniform(-10, 10)
            self.turbine_speed = int(self.thermal_power * 22 + random.uniform(-50, 50))
            self.generator_load = int(self.thermal_power * 12)
            
            # Rods drift slightly (realistic)
            if not self.is_auto:
                self.rods_position += random.uniform(-0.1, 0.1)
                self.rods_position = max(0, min(100, self.rods_position))
            
            # Circulation affects temperature
            self.circulation_flow = min(100, max(0, self.circulation_flow))
            if self.circulation_flow < 50:
                self.temperature += 2
            
            # Xenon builds up with power
            self.xenon_poisoning = 10.1 + (self.thermal_power / 5) + random.uniform(-0.5, 0.5)
            self.xenon_poisoning = min(35.0, self.xenon_poisoning)
            
            # Fuel burns slowly
            self.fuel_remaining -= 0.0001
            self.fuel_remaining = max(0, self.fuel_remaining)

class RBWRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BWR REACTOR SYSTEM V2")
        self.root.geometry("800x600")
        self.root.configure(bg='black')
        
        # Reactor simulation
        self.reactor = RBWRReactor()
        self.running = True
        
        # Custom fonts
        self.title_font = font.Font(family="Courier", size=16, weight="bold")
        self.label_font = font.Font(family="Courier", size=12)
        self.value_font = font.Font(family="Courier", size=12, weight="bold")
        
        self.setup_ui()
        self.start_simulation()
    
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg='black')
        header_frame.pack(pady=10)
        
        tk.Label(header_frame, text="#"*60, 
                 bg='black', fg='green', font=("Courier", 10)).pack()
        tk.Label(header_frame, text="# BWR REACTOR SYSTEM V2 ****", 
                 bg='black', fg='green', font=self.title_font).pack()
        tk.Label(header_frame, text="#"*60, 
                 bg='black', fg='green', font=("Courier", 10)).pack()
        
        # User label
        tk.Label(header_frame, text="User Logged: Supervisor", 
                 bg='black', fg='cyan', font=self.label_font).pack(pady=5)
        
        # Main display frame
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(pady=20)
        
        # Left column
        left_frame = tk.Frame(main_frame, bg='black')
        left_frame.grid(row=0, column=0, padx=40)
        
        # Right column  
        right_frame = tk.Frame(main_frame, bg='black')
        right_frame.grid(row=0, column=1, padx=40)
        
        # Create value displays
        self.value_vars = {}
        labels = [
            ("Reactor Thermal Power:", "power_var", " %"),
            ("Reactor Temperature:", "temp_var", " °C"),
            ("Reactor Pressure:", "pressure_var", " kPa"),
            ("Feedwater flow:", "flow_var", " kg/s"),
            ("Turbine speed:", "turbine_var", " RPM"),
            ("Generator load:", "load_var", " MW"),
            ("Rods position:", "rods_var", " %"),
            ("Circulation flow:", "circ_var", " %"),
            ("Xenon poisoning:", "xenon_var", " %"),
            ("Fuel Remaining:", "fuel_var", " %")
        ]
        
        # Left column labels
        for i, (text, var_name, unit) in enumerate(labels[:5]):
            self.create_display(left_frame, text, var_name, unit, i)
        
        # Right column labels
        for i, (text, var_name, unit) in enumerate(labels[5:]):
            self.create_display(right_frame, text, var_name, unit, i)
        
        # Control panel
        control_frame = tk.Frame(self.root, bg='black')
        control_frame.pack(pady=30)
        
        # Rod control
        rod_frame = tk.Frame(control_frame, bg='black')
        rod_frame.pack(pady=5)
        
        tk.Label(rod_frame, text="Control Rods:", 
                 bg='black', fg='white', font=self.label_font).pack(side=tk.LEFT)
        
        self.rod_scale = tk.Scale(rod_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                  length=200, bg='black', fg='white', 
                                  troughcolor='darkgray', highlightthickness=0)
        self.rod_scale.set(0)
        self.rod_scale.pack(side=tk.LEFT, padx=10)
        
        # Buttons
        button_frame = tk.Frame(control_frame, bg='black')
        button_frame.pack(pady=10)
        
        self.scram_button = tk.Button(button_frame, text="SCRAM REACTOR", 
                                      command=self.scram_reactor,
                                      bg='darkred', fg='white', 
                                      font=self.label_font, padx=20)
        self.scram_button.pack(side=tk.LEFT, padx=5)
        
        self.circ_button = tk.Button(button_frame, text="TOGGLE CIRCULATION", 
                                     command=self.toggle_circulation,
                                     bg='darkblue', fg='white', 
                                     font=self.label_font, padx=20)
        self.circ_button.pack(side=tk.LEFT, padx=5)
        
        self.auto_button = tk.Button(button_frame, text="AUTO MODE", 
                                     command=self.toggle_auto,
                                     bg='darkgreen', fg='white', 
                                     font=self.label_font, padx=20)
        self.auto_button.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Status: NORMAL")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              bg='black', fg='yellow', font=self.label_font)
        status_bar.pack(pady=10)
    
    def create_display(self, parent, text, var_name, unit, row):
        var = tk.StringVar(value="0.00")
        self.value_vars[var_name] = var
        
        frame = tk.Frame(parent, bg='black')
        frame.grid(row=row, column=0, pady=5, sticky='w')
        
        tk.Label(frame, text=text, 
                 bg='black', fg='white', font=self.label_font).pack(side=tk.LEFT)
        tk.Label(frame, textvariable=var, 
                 bg='black', fg='yellow', font=self.value_font).pack(side=tk.LEFT)
        tk.Label(frame, text=unit, 
                 bg='black', fg='white', font=self.label_font).pack(side=tk.LEFT)
    
    def start_simulation(self):
        def update_loop():
            while self.running:
                # Update reactor
                self.reactor.rods_position = self.rod_scale.get()
                self.reactor.update()
                
                # Update UI
                self.root.after(0, self.update_display)
                time.sleep(0.5)  # Update twice per second
        
        Thread(target=update_loop, daemon=True).start()
    
    def update_display(self):
        # Update all values
        self.value_vars["power_var"].set(f"{self.reactor.thermal_power:.4f}")
        self.value_vars["temp_var"].set(f"{self.reactor.temperature:.0f}")
        self.value_vars["pressure_var"].set(f"{self.reactor.pressure}")
        self.value_vars["flow_var"].set(f"{self.reactor.feedwater_flow:.1f}")
        self.value_vars["turbine_var"].set(f"{self.reactor.turbine_speed}")
        self.value_vars["load_var"].set(f"{self.reactor.generator_load}")
        self.value_vars["rods_var"].set(f"{self.reactor.rods_position:.2f}")
        self.value_vars["circ_var"].set(f"{self.reactor.circulation_flow}")
        self.value_vars["xenon_var"].set(f"{self.reactor.xenon_poisoning:.1f}")
        self.value_vars["fuel_var"].set(f"{self.reactor.fuel_remaining:.1f}")
        
        # Update rod scale (if not being dragged)
        if not self.reactor.is_scrammed:
            self.rod_scale.set(self.reactor.rods_position)
        
        # Update status
        if self.reactor.is_scrammed:
            self.status_var.set("Status: SCRAMMED - RODS INSERTING")
            self.scram_button.config(text="RESET SCRAM", bg='orange')
        else:
            if self.reactor.is_auto:
                self.status_var.set("Status: AUTO MODE ACTIVE")
                self.auto_button.config(bg='green')
            else:
                self.status_var.set("Status: MANUAL CONTROL")
                self.auto_button.config(bg='darkgreen')
            self.scram_button.config(text="SCRAM REACTOR", bg='darkred')
    
    def scram_reactor(self):
        if self.reactor.is_scrammed:
            # Reset SCRAM
            self.reactor.is_scrammed = False
            self.rod_scale.config(state=tk.NORMAL)
            self.circ_button.config(state=tk.NORMAL)
        else:
            # Initiate SCRAM
            self.reactor.is_scrammed = True
            self.reactor.is_auto = False
            self.rod_scale.config(state=tk.DISABLED)
            self.circ_button.config(state=tk.DISABLED)
    
    def toggle_circulation(self):
        if self.reactor.circulation_flow < 50:
            self.reactor.circulation_flow = 100
        else:
            self.reactor.circulation_flow = 0
    
    def toggle_auto(self):
        self.reactor.is_auto = not self.reactor.is_auto
    
    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RBWRApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
