"""
Vacancy Shadow Liability (VSL) Model

A model for estimating the public fiscal liability of vacant properties.
"""

from .loader import get_scenario_params, load_config, load_neighborhood_data
from .model import (
    calculate_direct_costs,
    calculate_foregone_tax_pv,
    calculate_vsl,
    generate_citywide_summary,
)

__version__ = "0.1.0"

__all__ = [
    "load_config",
    "get_scenario_params",
    "load_neighborhood_data",
    "calculate_direct_costs",
    "calculate_foregone_tax_pv",
    "calculate_vsl",
    "generate_citywide_summary",
]
