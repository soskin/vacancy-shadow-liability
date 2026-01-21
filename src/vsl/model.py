"""
VSL (Vacancy Shadow Liability) calculation model.

Computes:
1. Direct public costs attributable to vacancy
2. Foregone property tax revenue (present value over time)
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def calculate_direct_costs(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    """
    Calculate direct public costs attributable to vacancy.

    Direct costs include:
        - Fire response costs
        - Police response costs
        - Code enforcement costs
        - Demolition (amortized) costs
        - Blight remediation costs

    Args:
        df: DataFrame with neighborhood vacancy data.
        params: Scenario parameters from config.

    Returns:
        DataFrame with added direct cost columns.
    """
    result = df.copy()

    # Per-unit annual costs
    per_unit_cost = (
        params["fire_response_cost"]
        + params["police_response_cost"]
        + params["code_enforcement_cost"]
        + params["demolition_amortized_cost"]
        + params["blight_remediation_cost"]
    )

    # Apply spillover multiplier
    per_unit_cost *= params["spillover_multiplier"]

    # Total direct costs per neighborhood
    result["direct_cost_per_unit"] = per_unit_cost
    result["direct_cost_total"] = result["vacant_units"] * per_unit_cost

    return result


def calculate_foregone_tax_pv(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    """
    Calculate present value of foregone property tax revenue.

    Models the tax revenue that would have been collected if properties
    were occupied, accounting for:
        - Declining assessed values due to vacancy
        - Time value of money (discounting)

    Args:
        df: DataFrame with neighborhood vacancy data.
        params: Scenario parameters from config.

    Returns:
        DataFrame with added foregone tax columns.
    """
    result = df.copy()

    tax_rate = params["tax_rate"]
    decay_rate = params["assessment_decay_rate"]
    discount_rate = params["discount_rate"]
    years = params["projection_years"]

    # Calculate present value of foregone taxes for each neighborhood
    foregone_pv_list = []

    for _, row in result.iterrows():
        units = row["vacant_units"]
        base_value = row["avg_assessed_value"]
        years_already_vacant = row["years_vacant_avg"]

        # Current assessed value (already decayed)
        current_value = base_value * ((1 - decay_rate) ** years_already_vacant)

        # Calculate PV of foregone taxes over projection period
        pv_total = 0.0
        for year in range(1, years + 1):
            # Projected value continues to decay
            projected_value = current_value * ((1 - decay_rate) ** year)

            # Annual foregone tax per unit
            annual_tax = projected_value * tax_rate

            # Discount to present value
            pv_factor = 1 / ((1 + discount_rate) ** year)
            pv_total += annual_tax * pv_factor

        # Total for all units in neighborhood
        foregone_pv_list.append(pv_total * units)

    result["foregone_tax_pv"] = foregone_pv_list

    return result


def calculate_vsl(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    """
    Calculate total Vacancy Shadow Liability.

    Combines direct public costs and foregone tax revenue into
    a comprehensive liability estimate.

    Args:
        df: DataFrame with neighborhood vacancy data.
        params: Scenario parameters from config.

    Returns:
        DataFrame with all VSL calculations.
    """
    result = calculate_direct_costs(df, params)
    result = calculate_foregone_tax_pv(result, params)

    # Total VSL = direct costs + foregone tax (present value)
    result["total_vsl"] = result["direct_cost_total"] + result["foregone_tax_pv"]

    # Per-unit VSL for comparison
    result["vsl_per_unit"] = result["total_vsl"] / result["vacant_units"]

    return result


def generate_citywide_summary(df: pd.DataFrame, scenario: str) -> pd.DataFrame:
    """
    Generate citywide summary statistics.

    Args:
        df: DataFrame with neighborhood-level VSL calculations.
        scenario: Name of the scenario used.

    Returns:
        DataFrame with citywide summary metrics.
    """
    summary = {
        "scenario": scenario,
        "total_neighborhoods": len(df),
        "total_vacant_units": df["vacant_units"].sum(),
        "total_direct_costs": df["direct_cost_total"].sum(),
        "total_foregone_tax_pv": df["foregone_tax_pv"].sum(),
        "total_vsl": df["total_vsl"].sum(),
        "avg_vsl_per_unit": df["total_vsl"].sum() / df["vacant_units"].sum(),
        "max_neighborhood_vsl": df["total_vsl"].max(),
        "max_neighborhood_name": df.loc[df["total_vsl"].idxmax(), "neighborhood"],
    }

    return pd.DataFrame([summary])
