"""
Command-line interface for VSL model.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .loader import get_scenario_params, load_config, load_neighborhood_data
from .model import calculate_vsl, generate_citywide_summary


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="vsl",
        description="Vacancy Shadow Liability (VSL) Model",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the VSL model")
    run_parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="Path to input CSV file with neighborhood data",
    )
    run_parser.add_argument(
        "--scenario",
        "-s",
        type=str,
        default="base",
        choices=["low", "base", "high"],
        help="Scenario to use (default: base)",
    )
    run_parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path("config.yaml"),
        help="Path to config file (default: config.yaml)",
    )
    run_parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("data/outputs"),
        help="Output directory (default: data/outputs)",
    )

    return parser


def plot_by_neighborhood(df: pd.DataFrame, output_path: Path, scenario: str) -> None:
    """
    Create a bar chart showing VSL by neighborhood.

    Args:
        df: DataFrame with VSL calculations.
        output_path: Path to save the plot.
        scenario: Scenario name for the title.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    neighborhoods = df["neighborhood"]
    x = range(len(neighborhoods))

    # Stacked bar chart
    direct_costs = df["direct_cost_total"] / 1_000_000  # Convert to millions
    foregone_tax = df["foregone_tax_pv"] / 1_000_000

    bars1 = ax.bar(x, direct_costs, label="Direct Public Costs", color="#2ecc71")
    bars2 = ax.bar(
        x, foregone_tax, bottom=direct_costs, label="Foregone Tax (PV)", color="#3498db"
    )

    ax.set_xlabel("Neighborhood")
    ax.set_ylabel("VSL (Millions USD)")
    ax.set_title(f"Vacancy Shadow Liability by Neighborhood ({scenario.title()} Scenario)")
    ax.set_xticks(x)
    ax.set_xticklabels(neighborhoods, rotation=45, ha="right")
    ax.legend()

    # Add value labels on bars
    for i, (d, f) in enumerate(zip(direct_costs, foregone_tax)):
        total = d + f
        ax.annotate(
            f"${total:.2f}M",
            xy=(i, total),
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Plot saved to: {output_path}")


def run_model(args: argparse.Namespace) -> None:
    """Execute the VSL model with given arguments."""
    # Load configuration
    print(f"Loading config from: {args.config}")
    config = load_config(args.config)
    params = get_scenario_params(config, args.scenario)

    # Load input data
    print(f"Loading data from: {args.input}")
    df = load_neighborhood_data(args.input)
    print(f"Loaded {len(df)} neighborhoods")

    # Run calculations
    print(f"Running VSL model with '{args.scenario}' scenario...")
    results = calculate_vsl(df, params)
    summary = generate_citywide_summary(results, args.scenario)

    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Save outputs
    neighborhood_output = args.output_dir / "vsl_neighborhood.csv"
    summary_output = args.output_dir / "vsl_citywide_summary.csv"
    plot_output = args.output_dir / "vsl_by_neighborhood.png"

    results.to_csv(neighborhood_output, index=False)
    print(f"Neighborhood results saved to: {neighborhood_output}")

    summary.to_csv(summary_output, index=False)
    print(f"Citywide summary saved to: {summary_output}")

    plot_by_neighborhood(results, plot_output, args.scenario)

    # Print summary
    print("\n" + "=" * 50)
    print("CITYWIDE SUMMARY")
    print("=" * 50)
    print(f"Scenario: {args.scenario.upper()}")
    print(f"Total Vacant Units: {summary['total_vacant_units'].iloc[0]:,}")
    print(f"Total Direct Costs: ${summary['total_direct_costs'].iloc[0]:,.2f}")
    print(f"Total Foregone Tax (PV): ${summary['total_foregone_tax_pv'].iloc[0]:,.2f}")
    print(f"Total VSL: ${summary['total_vsl'].iloc[0]:,.2f}")
    print(f"Average VSL per Unit: ${summary['avg_vsl_per_unit'].iloc[0]:,.2f}")
    print(f"Highest Liability: {summary['max_neighborhood_name'].iloc[0]}")
    print("=" * 50)


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    if args.command == "run":
        run_model(args)
        return 0

    return 1
