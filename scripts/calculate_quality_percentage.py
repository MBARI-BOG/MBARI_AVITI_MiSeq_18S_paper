#!/usr/bin/env python3
"""
Calculate the percentage of bases with median quality score above specified thresholds
from a seven-number summary TSV file.
"""

import pandas as pd
import numpy as np
import argparse
import sys

def calculate_quality_percentage(tsv_file_path, quality_threshold=30):
    """
    Calculate the percentage of bases with median quality score above threshold.
    
    Parameters:
    -----------
    tsv_file_path : str
        Path to the TSV file containing quality score summaries
    quality_threshold : int, default=30
        Quality score threshold to compare against
        
    Returns:
    --------
    tuple
        (percentage, positions_above_threshold, total_positions)
    """
    
    # Read the TSV file
    df = pd.read_csv(tsv_file_path, sep='\t', index_col=0)
    
    # The median (50th percentile) is in the row with index '50%'
    median_row = df.loc['50%']
    
    # Count positions with median quality > threshold
    positions_above_threshold = (median_row > quality_threshold).sum()
    
    # Total number of positions
    total_positions = len(median_row)
    
    # Calculate percentage
    percentage = (positions_above_threshold / total_positions) * 100
    
    return percentage, positions_above_threshold, total_positions

def calculate_multiple_thresholds(tsv_file_path, quality_thresholds):
    """
    Calculate the percentage of bases with median quality score above multiple thresholds.
    
    Parameters:
    -----------
    tsv_file_path : str
        Path to the TSV file containing quality score summaries
    quality_thresholds : list
        List of quality score thresholds to compare against
        
    Returns:
    --------
    dict
        Dictionary with threshold as key and (percentage, positions_above, total_positions) as value
    """
    
    # Read the TSV file
    df = pd.read_csv(tsv_file_path, sep='\t', index_col=0)
    
    # The median (50th percentile) is in the row with index '50%'
    median_row = df.loc['50%']
    total_positions = len(median_row)
    
    results = {}
    
    for threshold in quality_thresholds:
        positions_above_threshold = (median_row > threshold).sum()
        percentage = (positions_above_threshold / total_positions) * 100
        results[threshold] = (percentage, positions_above_threshold, total_positions)
    
    return results

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate percentage of bases with median quality score above specified thresholds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python calculate_quality_percentage.py --thresholds 20 25 30 35
  python calculate_quality_percentage.py --thresholds 30 --file my_data.tsv
  python calculate_quality_percentage.py --thresholds 20 30 40 --file data.tsv --no-stats
        """
    )
    
    parser.add_argument(
        '--thresholds', '-t',
        nargs='+',
        type=int,
        required=True,
        help='Quality score thresholds to analyze (e.g., 20 25 30 35)'
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        default="/Users/katherine.silliman/Projects/NOAA/aviti_comp/forward-seven-number-summaries.tsv",
        help='Path to the TSV file containing quality score summaries (default: forward-seven-number-summaries.tsv)'
    )
    
    parser.add_argument(
        '--no-stats',
        action='store_true',
        help='Skip additional statistics and quality distribution output'
    )
    
    return parser.parse_args()

def main():
    """Main function to run the analysis."""
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Validate thresholds
    if not args.thresholds:
        print("Error: No quality thresholds provided. Use --thresholds to specify them.")
        sys.exit(1)
    
    if any(t < 0 for t in args.thresholds):
        print("Error: Quality thresholds must be non-negative integers.")
        sys.exit(1)
    
    # Calculate percentages for multiple thresholds
    results = calculate_multiple_thresholds(args.file, args.thresholds)
    
    print(f"Quality Score Analysis Results:")
    print(f"================================")
    print(f"Analysis of median quality scores across {results[args.thresholds[0]][2]} base positions")
    print(f"File: {args.file}")
    print()
    
    # Print results for each threshold
    print(f"{'Threshold':<10} {'Positions Above':<16} {'Percentage':<12}")
    print(f"{'-'*10} {'-'*16} {'-'*12}")
    
    for threshold in sorted(args.thresholds):
        percentage, positions_above, total_positions = results[threshold]
        print(f"Q{threshold:<9} {positions_above:<16} {percentage:.2f}%")
    
    # Show additional statistics unless --no-stats is specified
    if not args.no_stats:
        df = pd.read_csv(args.file, sep='\t', index_col=0)
        median_row = df.loc['50%']
        
        print(f"\nAdditional Statistics:")
        print(f"======================")
        print(f"Minimum median quality score: {median_row.min():.2f}")
        print(f"Maximum median quality score: {median_row.max():.2f}")
        print(f"Mean median quality score: {median_row.mean():.2f}")
        print(f"Standard deviation: {median_row.std():.2f}")
        
        # Show quality distribution
        print(f"\nQuality Score Distribution:")
        print(f"==========================")
        print(f"Positions with median quality 20-25: {((median_row >= 20) & (median_row < 25)).sum()}")
        print(f"Positions with median quality 25-30: {((median_row >= 25) & (median_row < 30)).sum()}")
        print(f"Positions with median quality 30-35: {((median_row >= 30) & (median_row < 35)).sum()}")
        print(f"Positions with median quality 35-40: {((median_row >= 35) & (median_row < 40)).sum()}")
        print(f"Positions with median quality < 20: {(median_row < 20).sum()}")
        print(f"Positions with median quality >= 40: {(median_row >= 40).sum()}")

if __name__ == "__main__":
    main()
