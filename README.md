# High-Performance Charged Particle Simulator

A 2D physics engine built with **C** for high-speed calculations and **Python (Matplotlib)** for a rich, interactive visualization. 

## 🚀 Overview
This project simulates the behavior of charged particles in a vacuum, subject to various physical fields. It demonstrates core physics concepts such as:
* **Lorentz Force:** Interaction with magnetic (B) and electric (E) fields.
* **Elastic Collisions:** Real-time $O(n^2)$ collision detection with varying masses.
* **Classical Mechanics:** Gravitational acceleration and boundary friction.

## 🛠️ Tech Stack
* **C (The Engine):** Handles the physics integration and collision logic for maximum performance.
* **Python (The UI):** Provides an interactive dashboard with sliders and real-time animation.
* **ctypes:** Bridges the high-level Python logic with the low-level C implementation.

## 📈 Key Features
* **Interactive Fields:** Adjust Gravity, E-Field, and B-Field on the fly.
* **Mass Heterogeneity:** Toggle between equal and random masses to observe momentum conservation.
* **Charge Dynamics:** Simulate mixed, positive, or neutral particle systems.
* **Vector Visualization:** Real-time arrows showing field directions and magnitudes.

## ⚙️ Installation & Running
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YourUsername/Charged-Particle-Simulator.git](https://github.com/YourUsername/Charged-Particle-Simulator.git)

## ⚙️ Compilation & Running
### Windows (MSYS2/MinGW)
```bash
gcc -shared -o engine.dll -fPIC src/engine.c
python main.py

# For Linux / macOS / Streamlit Cloud:
gcc -shared -o engine.so -fPIC src/engine.c
# Note: Ensure main.py loads 'engine.so' on these systems
python main.py