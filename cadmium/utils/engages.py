import numpy as np

def DrillEngage(x):
    # Drills only accept downward cutting
    # We tolerate upward cutting too
    return 1 if x % np.pi == 0 else 0