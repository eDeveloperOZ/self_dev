source ~/.zshrc

folder="$1"
scanned_folder=$(basename "$2")

# Count the number of files
echo "Estimating operations time"
num_files=$(find "$2" -type f | wc -l)

# Estimate time to process each file (you need to adjust this based on your observations)
time_per_file=0.012

# Calculate estimated total time
estimated_time=$(echo "$num_files * $time_per_file" | bc)

estimated_time=$(echo "$estimated_time / 10" | bc)
echo "Estimated time for completion: $estimated_time seconds"


output=$(fdupes -r "$2")
result=""
result_counter=0

# List of processed files
processed_files="$folder/processed_files.log"
touch "$processed_files"

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
            
            # Create the folder for the report
            report_folder="$folder/$scanned_folder/report$result_counter"
            mkdir -p "$report_folder"
            
            # Copy the file from the first path to the report folder
            cp "$first_path" "$report_folder/"
            
            # Create the .txt file with the list of paths
            path_count=$(echo "$result" | grep -c '^')
            path_list_file="$report_folder/number_of_locations$path_count.txt"
            echo "$result" > "$path_list_file"
            
            # Add the file to the processed files log
            echo "$first_path" >> "$processed_files"

            # echo "Report $result_counter generated for folder $scanned_folder"
            # echo
        fi
        result=""
    else
        result+="$line"$'\n'
    fi
done <<< "$output"
