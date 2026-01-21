# Vacancy Shadow Liability (VSL)

This project models vacant property as a public fiscal liability.

It estimates:
1. Direct public costs attributable to vacancy
2. Foregone property tax revenue due to delayed or suppressed use

The goal is to make vacancy legible to municipal finance, budgeting,
and housing strategy discussions.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the VSL model with the CLI:

```bash
python -m vsl run --input data/sample_neighborhoods.csv --scenario base
```

### CLI Options

```
python -m vsl run [OPTIONS]

Options:
  --input, -i PATH       Path to input CSV file (required)
  --scenario, -s TEXT    Scenario: low, base, or high (default: base)
  --config, -c PATH      Path to config file (default: config.yaml)
  --output-dir, -o PATH  Output directory (default: data/outputs)
```

### Scenarios

The model supports three scenarios configured in `config.yaml`:

| Scenario | Description |
|----------|-------------|
| `low`    | Conservative estimates of costs and tax impacts |
| `base`   | Moderate estimates (recommended default) |
| `high`   | Upper-bound estimates including spillover effects |

## Input Data Format

The input CSV must contain these columns:

| Column | Description |
|--------|-------------|
| `neighborhood` | Name of the neighborhood |
| `vacant_units` | Number of vacant units |
| `avg_assessed_value` | Average assessed value per unit (USD) |
| `years_vacant_avg` | Average years units have been vacant |

Example:
```csv
neighborhood,vacant_units,avg_assessed_value,years_vacant_avg
Downtown,45,185000,2.5
Westside,120,95000,4.2
```

## Outputs

The model generates three output files in `data/outputs/`:

1. **vsl_neighborhood.csv** - Detailed results per neighborhood
2. **vsl_citywide_summary.csv** - Aggregate citywide metrics
3. **vsl_by_neighborhood.png** - Bar chart visualization

## Model Components

### Direct Public Costs

Per-unit annual costs include:
- Fire response
- Police response
- Code enforcement
- Demolition (amortized)
- Blight remediation

### Foregone Tax Revenue

Calculates the present value of property taxes that would have been
collected if properties were occupied, accounting for:
- Declining assessed values due to vacancy
- Time value of money (discounting to present value)

## Configuration

Edit `config.yaml` to adjust model parameters for each scenario:
- Per-unit cost estimates
- Tax rates and assessment decay rates
- Discount rates for present value calculations
- Spillover multipliers for neighborhood effects

## Project Structure

```
vacancy-shadow-liability/
├── config.yaml              # Model parameters
├── requirements.txt         # Python dependencies
├── data/
│   ├── sample_neighborhoods.csv
│   └── outputs/
│       ├── vsl_neighborhood.csv
│       ├── vsl_citywide_summary.csv
│       └── vsl_by_neighborhood.png
└── src/
    └── vsl/
        ├── __init__.py
        ├── __main__.py      # Entry point
        ├── cli.py           # Command-line interface
        ├── loader.py        # Data loading utilities
        └── model.py         # VSL calculations
```
