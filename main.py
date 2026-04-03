
"""
    Charged Particle Simulator - Physics Engine with C Integration
    Author: Daniela
    Description: A high-performance 2D particle simulator calculating 
    gravity, electric, and magnetic fields using a C-based engine.
"""

import ctypes
import os
import subprocess
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# הגדרה חשובה ל-Streamlit: מונע מ-Matplotlib לנסות לפתוח חלון גרפי בשרת
import matplotlib
matplotlib.use('Agg') 

def compile_c_engine():
    """Compiles the C engine automatically if running on Linux (Streamlit Cloud)"""
    if os.name != 'nt':  # If NOT on Linux (Streamlit/Linux)
        if not os.path.exists("engine.so"):
            try:
                print("Compiling C engine for Linux...")
                subprocess.run(["gcc", "-shared", "-o", "engine.so", "-fPIC", "src/engine.c"], check=True)
            except Exception as e:
                st.error(f"Compilation failed: {e}")

# קריאה לפונקציית הקומפילציה לפני הכל
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
        self.dt = 0.005 
        
        # --- תיקון טעינת המנוע לפי מערכת הפעלה ---
        try:
            if os.name == 'nt': # Windows
                lib_name = "engine.dll"
            else: # Linux (Streamlit Cloud)
                lib_name = "engine.so"
            
            lib_path = os.path.abspath(lib_name)
            self.lib = ctypes.CDLL(lib_path)
            self._setup_c_interface()
        except Exception as e:
            st.error(f"Critical Error: Could not load C-Engine ({e})")
            st.stop() # עוצר את האפליקציה ב-Streamlit אם המנוע לא נטען

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
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        # ב-Streamlit הסליידרים של Matplotlib פחות נוחים, אבל נשמור על המבנה שלך
        plt.subplots_adjust(bottom=0.1) 
        
        self._init_visuals()
        
    def _init_visuals(self):
        self.ax.set_xlim(0, self.sim.width)
        self.ax.set_ylim(0, self.sim.height)
        
        colors = ['red' if p.charge > 0 else ('blue' if p.charge < 0 else 'gray') 
                  for p in self.sim.particles]
        self.scatter = self.ax.scatter([p.x for p in self.sim.particles], 
                                      [p.y for p in self.sim.particles],
                                      s=[p.radius**2 * 10 for p in self.sim.particles],
                                      c=colors, edgecolors='black', zorder=3)

    def update(self, frame, g, m, e):
        # הרצת 10 צעדי חישוב לכל פריים ויזואלי למהירות מירבית
        for _ in range(10):
            self.sim.lib.update_positions(
                self.sim.particles, self.sim.num_particles, ctypes.c_double(self.sim.dt),
                ctypes.c_double(self.sim.width), ctypes.c_double(self.sim.height),
                ctypes.c_double(g),
                ctypes.c_double(m),
                ctypes.c_double(e), 
                ctypes.c_double(0.0)
            )

        # עדכון המיקומים בגרף
        self.scatter.set_offsets(np.array([[p.x, p.y] for p in self.sim.particles]))
        return self.scatter,

# --- Streamlit Main Logic ---
if __name__ == "__main__":
    st.set_page_config(page_title="Physics Lab", layout="wide")
    st.title("⚛️ Advanced Particle Physics Laboratory")
    st.sidebar.header("Simulation Controls")
    
    # סליידרים ב-Sidebar של Streamlit (עובד הרבה יותר טוב בענן)
    g_val = st.sidebar.slider("Gravity", -20.0, 20.0, -9.8)
    e_val = st.sidebar.slider("Electric Field (E)", -30.0, 30.0, 0.0)
    b_val = st.sidebar.slider("Magnetic Field (B)", -15.0, 15.0, 0.0)
    
    # אתחול ב-Session State
    if 'sim' not in st.session_state:
        st.session_state.sim = ParticleSimulation(num_particles=40)
        st.session_state.app = SimulationApp(st.session_state.sim)

    plot_placeholder = st.empty()

    # לולאת האנימציה
    for frame in range(1000):
        # עדכון הפיזיקה עם הערכים מהסליידרים של Streamlit
        st.session_state.app.update(frame, g_val, b_val, e_val)
        
        # תצוגה
        with plot_placeholder.container():
            st.pyplot(st.session_state.app.fig)
        
        # השהייה קלה
        plt.pause(0.001)