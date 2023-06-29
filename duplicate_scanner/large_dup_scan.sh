#!/bin/zsh

# Check if a path is provided as an argument
if [[ $# -ne 1 ]]; then
  echo "Usage: ./scan_and_process.sh <path>"
  exit 1
fi

# Perform the find command and store the output in a file
find_output_file="disk_scan_output.txt"
find "$1" \( -name .Spotlight-V100 -o -name .Trashes \) -prune -o -type f -print > "$find_output_file"

# Activate the Python script with the find output
python3 ./process_files.py "$find_output_file"
