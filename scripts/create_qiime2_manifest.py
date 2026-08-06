#!/usr/bin/env python3
"""
Create a QIIME2 paired-end manifest file from FASTQ files.
Extracts sample ID from the first substring of the filename.
"""

import os
import glob
import pandas as pd
import argparse
from pathlib import Path

def extract_sample_id(filename):
    """
    Extract sample ID from filename by taking the first 2 substrings separated by underscores.
    
    Examples:
    - CN24F150mMV2_SC49_L1_R1.fastq.gz -> CN24F150mMV2_SC49
    - 14223c01_01c_eDNA_L1_R1.fastq.gz -> 14223c01_01c
    - Art_Comm_FWAQ_L1_R1.fastq.gz -> Art_Comm
    """
    # Remove .fastq.gz extension and get the base name
    base_name = filename.replace('.fastq.gz', '')
    
    # Split by underscore and take the first 2 parts
    parts = base_name.split('_')
    if len(parts) >= 2:
        sample_id = '_'.join(parts[:2])
    else:
        # If there's only one part, use it as is
        sample_id = parts[0]
    
    return sample_id

def find_fastq_pairs(directory):
    """
    Find paired FASTQ files in a directory and return a list of tuples.
    Each tuple contains (sample_id, forward_file, reverse_file)
    """
    # Find all R1 files - handle both patterns: *_R1.fastq.gz and *_R1_001.fastq.gz
    r1_patterns = [
        os.path.join(directory, "*_R1.fastq.gz"),
        os.path.join(directory, "*_R1_001.fastq.gz")
    ]
    
    r1_files = []
    for pattern in r1_patterns:
        r1_files.extend(glob.glob(pattern))
    
    pairs = []
    
    for r1_file in r1_files:
        # Determine the pattern and construct R2 filename
        if r1_file.endswith('_R1_001.fastq.gz'):
            base_name = r1_file.replace('_R1_001.fastq.gz', '')
            r2_file = base_name + '_R2_001.fastq.gz'
        elif r1_file.endswith('_R1.fastq.gz'):
            base_name = r1_file.replace('_R1.fastq.gz', '')
            r2_file = base_name + '_R2.fastq.gz'
        else:
            print(f"Warning: Unrecognized R1 file pattern: {r1_file}")
            continue
        
        # Check if the corresponding R2 file exists
        if os.path.exists(r2_file):
            # Extract sample ID from R1 filename
            filename = os.path.basename(r1_file)
            sample_id = extract_sample_id(filename)
            
            pairs.append((sample_id, r1_file, r2_file))
        else:
            print(f"Warning: No corresponding R2 file found for {r1_file}")
    
    return pairs

def create_manifest(directory, output_file):
    """
    Create a QIIME2 paired-end manifest file.
    """
    # Find all paired FASTQ files
    pairs = find_fastq_pairs(directory)
    
    if not pairs:
        print(f"No paired FASTQ files found in {directory}")
        return
    
    # Create DataFrame for manifest
    manifest_data = []
    
    for sample_id, r1_file, r2_file in pairs:
        # Convert to absolute paths
        r1_abs = os.path.abspath(r1_file)
        r2_abs = os.path.abspath(r2_file)
        
        manifest_data.append({
            'sample-id': sample_id,
            'forward-absolute-filepath': r1_abs,
            'reverse-absolute-filepath': r2_abs
        })
    
    # Create DataFrame and sort by sample-id
    manifest_df = pd.DataFrame(manifest_data)
    manifest_df = manifest_df.sort_values('sample-id')
    
    # Save to TSV file
    manifest_df.to_csv(output_file, sep='\t', index=False)
    
    print(f"Created QIIME2 manifest file: {output_file}")
    print(f"Found {len(pairs)} paired samples:")
    
    for sample_id, r1_file, r2_file in sorted(pairs):
        print(f"  {sample_id}: {os.path.basename(r1_file)} + {os.path.basename(r2_file)}")
    
    return manifest_df

def main():
    """Main function to create the manifest file."""
    parser = argparse.ArgumentParser(
        description="Create a QIIME2 paired-end manifest file from FASTQ files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_qiime2_manifest.py --directory /path/to/fastq/files --output manifest.tsv
  python create_qiime2_manifest.py --directory raw_data/FD_20250210_BAK16171_18S_PE150 --output manifest.tsv
        """
    )
    
    parser.add_argument(
        '--directory', '-d',
        type=str,
        required=True,
        help='Directory containing FASTQ files'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='qiime2_manifest.tsv',
        help='Output manifest file name (default: qiime2_manifest.tsv)'
    )
    
    args = parser.parse_args()
    
    # Check if directory exists
    if not os.path.exists(args.directory):
        print(f"Error: Directory {args.directory} does not exist")
        return
    
    # Create the manifest
    manifest_df = create_manifest(args.directory, args.output)
    
    if manifest_df is not None:
        print(f"\nManifest file created successfully!")
        print(f"Total samples: {len(manifest_df)}")
        print(f"File saved as: {os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()
