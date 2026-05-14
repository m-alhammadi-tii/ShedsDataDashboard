from datetime import time

DEFAULT_DAY_START = time(9, 30)
DEFAULT_DAY_END = time(15, 30)

INTERNAL_GROUPS = {
    "T1": ["R-T1", "C-T1", "TII-T1"],
    "T2": ["R-T2", "C-T2", "TII-T2"],
    "T3": ["R-T3", "C-T3", "TII-T3"],
    "T4": ["R-T4", "C-T4", "TII-T4"],
    "H1": ["R-H1", "C-H1", "TII-H1"],
    "H2": ["R-H2", "C-H2", "TII-H2"],
    "H3": ["R-H3", "C-H3", "TII-H3"],
    "H4": ["R-H4", "C-H4", "TII-H4"],
}

SHEDS_GROUPS = {
    "O1": ["R-TCO1", "C-TCO1", "TII-TCO1"],
    "O2": ["R-TCO2", "C-TCO2", "TII-TCO2"],
    "O3": ["R-TCO3", "C-TCO3", "TII-TCO3"],
    "O4": ["R-TCO4", "C-TCO4", "TII-TCO4"],
    "O5": ["R-TCO5", "C-TCO5", "TII-TCO5"],
    "I1": ["R-TCI1", "C-TCI1", "TII-TCI1"],
    "I2": ["R-TCI2", "C-TCI2", "TII-TCI2"],
    "I3": ["R-TCI3", "C-TCI3", "TII-TCI3"],
    "I4": ["R-TCI4", "C-TCI4", "TII-TCI4"],
    "I5": ["R-TCI5", "C-TCI5", "TII-TCI5"],
    "I6": ["R-TCI6", "C-TCI6", "TII-TCI6"],
}

INTERNAL_TEMP_KEYS = ["T1", "T2", "T3", "T4"]
INTERNAL_HUMIDITY_KEYS = ["H1", "H2", "H3", "H4"]
EXTERNAL_SURFACE_KEYS = ["O1", "O2", "O3", "O4", "O5"]
INTERNAL_SURFACE_KEYS = ["I1", "I2", "I3", "I4", "I5", "I6"]

SHED_NAMES = ["R", "C", "TII"]
DELTA_FORMULAS = {
    "ΔT1": ("TII - C", "TII", "C"),
    "ΔT2": ("TII - R", "TII", "R"),
    "ΔT3": ("C - R", "C", "R"),
}
