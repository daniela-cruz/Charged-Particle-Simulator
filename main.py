"""
    Charged Particle Simulator - Physics Engine with C Integration
    Author: Daniela
    Description: A high-performance 2D particle simulator calculating 
    gravity, electric, and magnetic fields using a C-based engine.
"""


import ctypes
import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.animation import FuncAnimation



def compile_c_engine():
    """Compiles the C engine automatically if running on Linux (Streamlit Cloud)"""
    if os.name != 'nt':  # If NOT on Windows (i.e., Linux/Streamlit)
        if not os.path.exists("engine.so"):
            print("Compiling C engine for Linux...")
            subprocess.run(["gcc", "-shared", "-o", "engine.so", "-fPIC", "src/engine.c"], check=True)

# Call the compilation function
compile_c_engine()

# --- C-Engine Structure Definition ---
class Particle(ctypes.Structure):
    """ Matches the C-struct definition for memory-mapping """
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("vx", ctypes.c_double),
        ("vy", ctypes.c_double),
        ("radius", ctypes.c_double),
        ("mass", ctypes.c_double),
        ("charge", ctypes.c_double)
    ]

class ParticleSimulation:
    def __init__(self, num_particles=40, width=100.0, height=100.0):
        self.num_particles = num_particles
        self.width = width
        self.height = height
        self.dt = 0.005 # Simulation time-step
        
        try:
            lib_path = os.path.abspath("engine.dll")
            self.lib = ctypes.CDLL(lib_path)
            self._setup_c_interface()
        except Exception as e:
            print(f"Error loading C-Engine: {e}")
            exit()

        self.particles = (Particle * num_particles)()
        self._init_particles()

    def _setup_c_interface(self):
        self.lib.update_positions.argtypes = [
            ctypes.POINTER(Particle), ctypes.c_int, ctypes.c_double,
            ctypes.c_double, ctypes.c_double, ctypes.c_double,
            ctypes.c_double, ctypes.c_double, ctypes.c_double
        ]

    def _init_particles(self, mass=1.0, charge_mode='Mixed (+/-)'):
        for i, p in enumerate(self.particles):
            p.x, p.y = np.random.uniform(10, self.width-10, 2)
            p.vx, p.vy = np.random.uniform(-8, 8, 2)
            p.mass = mass
            p.radius = np.sqrt(mass) * 1.5
            
            if charge_mode == 'All Neutral': p.charge = 0.0
            elif charge_mode == 'All Positive': p.charge = 1.0
            else: p.charge = 1.0 if i % 2 == 0 else -1.0

# --- UI & Visualization Class ---
class SimulationApp:
    def __init__(self, sim):
        self.sim = sim
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.35, right=0.75)
        
        self._init_ui()
        self._init_visuals()
        
    def _init_visuals(self):
        self.ax.set_xlim(0, self.sim.width)
        self.ax.set_ylim(0, self.sim.height)
        self.ax.set_title("Advanced Particle Physics Laboratory", fontsize=14, pad=20)
        
        colors = ['red' if p.charge > 0 else ('blue' if p.charge < 0 else 'gray') 
                  for p in self.sim.particles]
        self.scatter = self.ax.scatter([p.x for p in self.sim.particles], 
                                      [p.y for p in self.sim.particles],
                                      s=[p.radius**2 * 10 for p in self.sim.particles],
                                      c=colors, edgecolors='black', zorder=3)

        self.q_grav = self.ax.quiver(10, 90, 0, 0, color='green', scale=100, width=0.01)
        self.q_elec = self.ax.quiver(50, 90, 0, 0, color='orange', scale=50, width=0.015)
        self.mag_ind = self.ax.plot([], [], 'X', color='darkblue', markersize=12)[0]
        
        self.ax.text(10, 95, "Gravity", color='green', ha='center', fontweight='bold')
        self.ax.text(50, 95, "Electric (E)", color='orange', ha='center', fontweight='bold')
        self.ax.text(90, 95, "Magnetic (B)", color='darkblue', ha='center', fontweight='bold')

    def _init_ui(self):
        # Sliders
        self.ax_g = plt.axes([0.15, 0.22, 0.4, 0.02])
        self.ax_e = plt.axes([0.15, 0.17, 0.4, 0.02])
        self.ax_b = plt.axes([0.15, 0.12, 0.4, 0.02])
        self.ax_m = plt.axes([0.15, 0.07, 0.4, 0.02])

        self.s_grav = Slider(self.ax_g, 'Gravity ', -20.0, 20.0, valinit=-9.8, color='green')
        self.s_elec = Slider(self.ax_e, 'E-Field ', -30.0, 30.0, valinit=0.0, color='orange')
        self.s_mag  = Slider(self.ax_b, 'B-Field ', -15.0, 15.0, valinit=0.0, color='darkblue')
        self.s_mass = Slider(self.ax_m, 'Base Mass ', 0.1, 50.0, valinit=1.0, color='gray')

        # Radio Buttons
        self.ax_radio_q = plt.axes([0.78, 0.15, 0.15, 0.12])
        self.radio_q = RadioButtons(self.ax_radio_q, ('Mixed (+/-)', 'All Positive', 'All Neutral'))

        self.ax_radio_m = plt.axes([0.78, 0.05, 0.15, 0.08])
        self.radio_m = RadioButtons(self.ax_radio_m, ('Equal Mass', 'Random Masses'))

        # Reset Button
        self.ax_reset = plt.axes([0.78, 0.30, 0.15, 0.05])
        self.btn_reset = Button(self.ax_reset, 'Apply & Reset', color='whitesmoke', hovercolor='lightblue')
        self.btn_reset.on_clicked(self.reset)

        # Persistence (Keep references alive)
        self.ui_elements = [self.s_grav, self.s_elec, self.s_mag, self.s_mass, 
                           self.radio_q, self.radio_m, self.btn_reset]

    def reset(self, event):
        m_mode = self.radio_m.value_selected
        q_mode = self.radio_q.value_selected
        base_m = self.s_mass.val

        for i, p in enumerate(self.sim.particles):
            p.x, p.y = np.random.uniform(10, self.sim.width-10, 2)
            p.vx, p.vy = np.random.uniform(-8, 8, 2)
            
            if m_mode == 'Random Masses':
                p.mass = base_m * np.random.uniform(0.5, 3.0)
            else:
                p.mass = base_m
                
            p.radius = np.sqrt(p.mass) * 1.5
            
            if q_mode == 'All Neutral': p.charge = 0.0
            elif q_mode == 'All Positive': p.charge = 1.0
            else: p.charge = 1.0 if i % 2 == 0 else -1.0

        new_colors = ['red' if p.charge > 0 else ('blue' if p.charge < 0 else 'gray') for p in self.sim.particles]
        self.scatter.set_color(new_colors)
        self.scatter.set_sizes([p.radius**2 * 10 for p in self.sim.particles])
        self.fig.canvas.draw_idle()

    def update(self, frame):
        for _ in range(10):
            self.sim.lib.update_positions(
                self.sim.particles, self.sim.num_particles, ctypes.c_double(self.sim.dt),
                self.sim.width, self.sim.height,
                ctypes.c_double(self.s_grav.val),
                ctypes.c_double(self.s_mag.val),
                ctypes.c_double(self.s_elec.val), 
                ctypes.c_double(0.0)
            )

        self.q_grav.set_UVC(0, self.s_grav.val)
        self.q_elec.set_UVC(self.s_elec.val, 0)
        
        b_val = self.s_mag.val
        if abs(b_val) > 0.1:
            self.mag_ind.set_data([90], [90])
            self.mag_ind.set_marker('X' if b_val > 0 else 'o')
        else:
            self.mag_ind.set_data([], [])

        self.scatter.set_offsets(np.array([[p.x, p.y] for p in self.sim.particles]))
        return self.scatter, self.q_grav, self.q_elec, self.mag_ind

    def run(self):
        self.ani = FuncAnimation(self.fig, self.update, interval=15, blit=True)
        plt.show()

if __name__ == "__main__":
    simulation = ParticleSimulation(num_particles=50)
    app = SimulationApp(simulation)
    app.run()