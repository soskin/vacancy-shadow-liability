"""
Data loading utilities for VSL model.

Handles loading neighborhood CSV data and configuration parameters.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def load_config(config_path: Path) -> dict[str, Any]:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the config.yaml file.

    Returns:
        Dictionary containing all configuration parameters.

    Raises:
        FileNotFoundError: If config file does not exist.
        yaml.YAMLError: If config file is malformed.
    """
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_scenario_params(config: dict[str, Any], scenario: str) -> dict[str, Any]:
    """
    Extract parameters for a specific scenario.

    Args:
        config: Full configuration dictionary.
        scenario: One of 'low', 'base', or 'high'.

    Returns:
        Dictionary of parameters for the specified scenario.

    Raises:
        KeyError: If scenario is not found in config.
    """
    if scenario not in config["scenarios"]:
        valid = list(config["scenarios"].keys())
        raise KeyError(f"Unknown scenario '{scenario}'. Valid options: {valid}")
    return config["scenarios"][scenario]


def load_neighborhood_data(csv_path: Path) -> pd.DataFrame:
    """
    Load neighborhood-level vacancy data from CSV.

    Expected columns:
        - neighborhood: Name of the neighborhood
        - vacant_units: Number of vacant units
        - avg_assessed_value: Average assessed value per unit (USD)
        - years_vacant_avg: Average years units have been vacant

    Args:
        csv_path: Path to the input CSV file.

    Returns:
        DataFrame with validated neighborhood data.

    Raises:
        FileNotFoundError: If CSV file does not exist.
        ValueError: If required columns are missing.
    """
    df = pd.read_csv(csv_path)

    required_columns = [
        "neighborhood",
        "vacant_units",
        "avg_assessed_value",
        "years_vacant_avg",
    ]

    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Ensure numeric types
    df["vacant_units"] = pd.to_numeric(df["vacant_units"], errors="coerce")
    df["avg_assessed_value"] = pd.to_numeric(df["avg_assessed_value"], errors="coerce")
    df["years_vacant_avg"] = pd.to_numeric(df["years_vacant_avg"], errors="coerce")

    # Drop rows with invalid data
    initial_count = len(df)
    df = df.dropna(subset=required_columns)
    if len(df) < initial_count:
        dropped = initial_count - len(df)
        print(f"Warning: Dropped {dropped} rows with missing/invalid data")

    return df
