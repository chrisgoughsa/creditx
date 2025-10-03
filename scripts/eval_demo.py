#!/usr/bin/env python3
"""
Evaluation demo script for CreditX pricing suggestions.

Loads sample submissions data, calls pricing functions directly,
and displays results in a sortable table format.
"""

import sys
from pathlib import Path
import polars as pl
from rich.console import Console
from rich.table import Table
from rich import box

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.features import prepare_submissions_features
from app.pricing import suggest_rate, price_band


def load_sample_data(csv_path: str) -> pl.DataFrame:
    """Load and prepare sample submissions data."""
    print(f"Loading sample data from: {csv_path}")
    
    # Read CSV file
    df = pl.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from CSV")
    
    # Filter out empty rows (where submission_id is null)
    df = df.filter(pl.col("submission_id").is_not_null())
    print(f"Filtered to {len(df)} valid submissions")
    
    # Convert to list of dicts for feature preparation
    submissions_data = df.to_dicts()
    
    # Prepare features using the same function as the API
    features_df = prepare_submissions_features(submissions_data)
    
    return features_df


def calculate_pricing_suggestions(df: pl.DataFrame) -> pl.DataFrame:
    """Calculate pricing suggestions for all submissions."""
    results = []
    
    for row in df.iter_rows(named=True):
        # Get suggested rate and adjustments
        suggested_rate, adjustments = suggest_rate(row)
        
        # Determine risk band
        band = price_band(suggested_rate)
        
        results.append({
            "id": row["submission_id"],
            "rate_bps": suggested_rate,
            "band": band,
            "sector": row["sector"],
            "exposure_limit": row["exposure_limit"],
            "debtor_days": row["debtor_days"],
            "financials_attached": row["financials_attached"],
            "years_trading": row["years_trading"],
            "broker_hit_rate": row["broker_hit_rate"],
            "has_judgements": row["has_judgements"],
            "adjustments": adjustments
        })
    
    return pl.DataFrame(results)


def create_pretty_table(df: pl.DataFrame) -> Table:
    """Create a rich table for displaying results."""
    table = Table(title="CreditX Pricing Suggestions", box=box.ROUNDED)
    
    # Add columns
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Rate (bps)", style="magenta", justify="right")
    table.add_column("Band", style="green", justify="center")
    table.add_column("Sector", style="blue")
    table.add_column("Exposure", style="yellow", justify="right")
    table.add_column("Debtor Days", style="yellow", justify="right")
    table.add_column("Financials", style="green" if True else "red", justify="center")
    table.add_column("Years Trading", style="yellow", justify="right")
    table.add_column("Broker Hit Rate", style="cyan", justify="right")
    table.add_column("Judgements", style="red" if True else "green", justify="center")
    
    # Add rows
    for row in df.iter_rows(named=True):
        table.add_row(
            str(row["id"]),
            str(row["rate_bps"]),
            str(row["band"]),
            str(row["sector"]),
            f"{row['exposure_limit']:,.0f}",
            str(row["debtor_days"]),
            "✓" if row["financials_attached"] else "✗",
            str(row["years_trading"]),
            f"{row['broker_hit_rate']:.2f}",
            "✓" if row["has_judgements"] else "✗"
        )
    
    return table


def print_summary_stats(df: pl.DataFrame):
    """Print summary statistics."""
    console = Console()
    
    # Basic stats
    console.print("\n[bold]Summary Statistics:[/bold]")
    console.print(f"Total submissions: {len(df)}")
    console.print(f"Rate range: {df['rate_bps'].min()} - {df['rate_bps'].max()} bps")
    console.print(f"Average rate: {df['rate_bps'].mean():.1f} bps")
    
    # Band distribution
    band_counts = df.group_by("band").agg(pl.len().alias("count")).sort("band")
    console.print(f"\n[bold]Risk Band Distribution:[/bold]")
    for row in band_counts.iter_rows(named=True):
        console.print(f"  {row['band']}: {row['count']} submissions")
    
    # Sector breakdown
    sector_stats = df.group_by("sector").agg([
        pl.len().alias("count"),
        pl.col("rate_bps").mean().alias("avg_rate"),
        pl.col("rate_bps").min().alias("min_rate"),
        pl.col("rate_bps").max().alias("max_rate")
    ]).sort("avg_rate")
    
    console.print(f"\n[bold]Sector Analysis:[/bold]")
    for row in sector_stats.iter_rows(named=True):
        console.print(f"  {row['sector']}: {row['count']} subs, "
                    f"avg {row['avg_rate']:.0f} bps "
                    f"(range: {row['min_rate']}-{row['max_rate']} bps)")


def main():
    """Main evaluation function."""
    console = Console()
    
    # Path to sample data
    sample_data_path = Path(__file__).parent.parent / "sample_data" / "submissions.csv"
    
    if not sample_data_path.exists():
        console.print(f"[red]Error: Sample data file not found at {sample_data_path}[/red]")
        return 1
    
    try:
        # Load and prepare data
        features_df = load_sample_data(str(sample_data_path))
        
        # Calculate pricing suggestions
        console.print("\nCalculating pricing suggestions...")
        results_df = calculate_pricing_suggestions(features_df)
        
        # Sort by rate (ascending - lowest risk first)
        results_df = results_df.sort("rate_bps")
        
        # Display results
        table = create_pretty_table(results_df)
        console.print(table)
        
        # Print summary statistics
        print_summary_stats(results_df)
        
        # Show some examples of adjustments
        console.print(f"\n[bold]Sample Adjustments:[/bold]")
        for i, row in enumerate(results_df.head(3).iter_rows(named=True)):
            console.print(f"\n[cyan]{row['id']}[/cyan] ({row['band']}, {row['rate_bps']} bps):")
            for adjustment in row['adjustments']:
                console.print(f"  • {adjustment}")
        
        return 0
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


if __name__ == "__main__":
    exit(main())
