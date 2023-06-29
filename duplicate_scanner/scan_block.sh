#!/bin/bash

# Set the block directory path from the command line argument
block_dir="$1"

# Set the base directory for the reports from the command line argument
report_base_dir="$2"

# Create a name for the block from the directory path
block_name=$(basename "$block_dir")

mkdir -p "$report_base_dir"

# List of processed files
processed_files="$report_base_dir/processed_files.log"
touch "$processed_files"

# Use fdupes to find duplicates
output=$(fdupes -r "$block_dir")
result=""
result_counter=0

# Process the output of fdupes
while IFS= read -r line; do
    if [[ -z $line ]]; then
        if [[ -n $result ]]; then
            first_path=$(echo "$result" | head -n 1)

            # Skip if the file has been processed before
            if grep -Fxq "$first_path" "$processed_files"; then
                result=""
                continue
            fi

            ((result_counter++))
            
            # Create the directory for the report
            report_dir="$report_base_dir/report$result_counter"
            mkdir -p "$report_dir"
            
            # Copy the file from the first path to the report directory
            cp "$first_path" "$report_dir/"
            
            # Create the .txt file with the list of paths
            path_count=$(echo "$result" | grep -c '^')
            path_list_file="$report_dir/number_of_locations$path_count.txt"
            echo "$result" > "$path_list_file"
            
            # Add the file to the processed files log
            echo "$first_path" >> "$processed_files"
        fi
        result=""
    else
        result+="$line"$'\n'
    fi
done <<< "$output"
