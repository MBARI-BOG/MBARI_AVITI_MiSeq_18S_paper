#!/bin/bash
# USAGE - Instead of running as a bash script, I just copied and pasted the for loop into the terminal when in the AVITI directory. A little modification will likely need to be made to make it a proper bash script.
# NOTE: THIS SCRIPT IS SPECIFICALLY FOR THE AVITI PLATE FK. This script is used to subsample raw .fastq files from the larger AVITI plate to match the same number of reads that were obtained per sample when the library was sequenced on the MiSeq. 

for folder in {1..95} #set up for loop to loop into the AVITI library folders # {1..95}
do
  cd FK${folder} #cd into each library folder in a loop
  echo "********"
  echo "Diving into AVITI library FK"${folder}
  for file in *.fastq.gz
  do
    # file_name=*${file}.fastq.gz
    output_name=subsampled_${file}
    echo "*Input AVITI file: " $file
    echo "**Subsampled output filename: " $output_name
    lines=$(gunzip -c /Volumes/mbon/raw_sequence_data/18S/FD_20250210_BAK16171_18S_PE150/FD${folder}/*_R1_001.fastq.gz | wc -l)
    echo "***MiSeq file lines: " $lines
    reads=$((lines/4))
    echo "****MiSeq file reads to truncate AVITI file to: " $reads
    # seqkit sample -n ${reads} -s 100 ${file} -o $output_name
    seqkit sample -n ${reads} -s 100 ${file} -o /Volumes/mbon/analysis/AVITI_vs_MiSeq/plate_FK_subsampled/FK${folder}/$output_name
  done
  cd ../
  echo "Done with AVITI library FK"${folder}
  echo "********"
done
