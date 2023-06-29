import os
import collections
import sys
import subprocess

# Check if a path is provided as an argument
if len(sys.argv) != 2:
    print("Usage: python3 process_files.py <file>")
    exit(1)

# Step 1
with open(sys.argv[1], 'r') as f:
    lines = f.readlines()

# Step 2
grade_dict = {}

# Step 3
for line in lines:
    path = line.strip()
    extension = os.path.splitext(path)[-1].lower()
    depth = path.count('/')
    directory_name = os.path.dirname(path).split('/')[-1]
    file_name = os.path.basename(path)

    efs = 1 if extension in ['.txt', '.log', '.csv', '.html', '.json'] else 2 if extension in ['.jpg', '.png', '.pdf', '.docx'] else 3
    dd = 1 / depth
    dnf = 1 if directory_name in ['backup', 'copy', 'old', 'archive', 'duplicate'] else 0.5
    fnf = 1 if 'copy' in file_name or 'backup' in file_name or 'duplicate' in file_name else 0.5
    cpf = 1  # This should be calculated based on the frequency of the directory paths in the scan output

    grade = efs * dd * dnf * fnf * cpf

    grade_dict[path] = grade

# Step 4
block_grades = collections.defaultdict(list)

for path, grade in grade_dict.items():
    directory_path = os.path.dirname(path)
    block_grades[directory_path].append(grade)

# Step 5
for block, grades in block_grades.items():
    block_grades[block] = sum(grades) / len(grades)

# Step 6
sorted_blocks = sorted(block_grades.items(), key=lambda x: x[1], reverse=True)

# Define path to output directory for reports
output_dir = '/Users/ofirozeri/development/playground/folder_scanner/external_reports'  # replace with actual path

# Step 7
for block, grade in sorted_blocks:
    # Get the files in the block directory
    files = [f for f in grade_dict if os.path.dirname(f) == block]

    # Sort the files within the block based on their individual grades
    sorted_files = sorted(files, key=lambda x: grade_dict[x], reverse=True)

    # print(f"Scanning block: {block} with grade: {grade}")
    # print(f"Files to scan in the block sorted by their grades: {sorted_files}")

    # Perform duplicate scanning on the files within the block
    print(f"Scanning block: {block}\n\n")
    # Replace './scan_block.sh' with the path to your actual script
    # script_path = './scan_block.sh' 
    # result = subprocess.run([script_path, block, output_dir], capture_output=True, text=True)

    # if result.returncode != 0:
    #     print(f'Error running script: {result.stderr}')
    # else:
    #     print(f'Script output: {result.stdout}\n\n')

# Step 8
remaining_files = [f for f in grade_dict if os.path.dirname(f) not in block_grades.keys()]

print("Scanning remaining files:")
for file in remaining_files:
    print(f"Scanning file: {file}")