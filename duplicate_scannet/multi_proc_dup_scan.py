import os
import hashlib
import sys
import time
import psutil
import resource
import tracemalloc
from multiprocessing import Pool, cpu_count, Value
import multiprocessing
size_left = multiprocessing.Value('L', int(451.24 * 1024 ** 3))  # 'L' indicates a long integer


# ANSI escape sequence for red color
RED = "\033[91m"
END = "\033[0m"
# ANSI escape sequence for yellow color
YELLOW = "\033[93m"
# ANSI escape sequence for bold text
BOLD = "\033[1m"
# ANSI escape sequence to reset color and text formatting
RESET = "\033[0m"


# Maximum size of the hash dictionary
MAX_DICT_SIZE = 5000


def enable_tracemalloc():
    tracemalloc.start()


def print_memory_usage():
    global size_left 
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    memory_usage = memory_info.rss / 1024 ** 2
    memory_usage_formatted = f"{memory_usage:.2f} MB"
    colored_memory_usage = f"{RED}{memory_usage_formatted}{END}"
    print(f"Memory usage: {colored_memory_usage}")

    peak_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_memory_usage = peak_memory / 1024
    peak_memory_usage_formatted = f"{peak_memory_usage:.2f} MB"
    colored_peak_memory_usage = f"{RED}{peak_memory_usage_formatted}{END}"
    print(f"Peak memory usage: {colored_peak_memory_usage}")
    

    print("Memory breakdown:")
    for name, size in memory_info._asdict().items():
        size_mb = size / 1024 ** 2
        print(f"  {name}: {size_mb:.2f} MB")
        

    print("Memory usage by object:")
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    for index, stat in enumerate(top_stats):
        size_mb = stat.size / 1024 ** 2
        if size_mb > 00.01:
            traceback_str = "\n".join(stat.traceback.format())
            print(f"  Object {index+1}: Size: {size_mb:.2f} MB\n{traceback_str}\n")


def worker(args):
    global size_left
    filepath, hashes, hash_file_path = args
    filehash = hash_file(filepath, hashes, hash_file_path)
    filesize = os.path.getsize(filepath)
    with size_left.get_lock():
        size_left.value -= filesize
        if size_left.value % (1000 * 1024 ** 2) == 0:
            print(f"{RED}Size left: {size_left.value / 1024 ** 2} MB") # Print what's left
    return (filehash, filepath)



def hash_file(filepath, hashes, hash_file_path):
    try:
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            try:
                for block in iter(lambda: f.read(4096), b''):
                    hasher.update(block)
            except TypeError as te:
                block = f.read(4096)
                print(f"TypeError while processing file {filepath}: {te}")
                print(f"Block: {block}")
                print(f"Type of block: {type(block)}")
        filehash = hasher.hexdigest()
        if filehash not in hashes:
            add_hash_to_file(filehash, hash_file_path)
        return filehash
    except Exception as e:
        print(f"Error hashing file {filepath}: {e}")
        return None


def add_hash_to_file(filehash, hash_file):
    with open(hash_file, 'a') as f:
        f.write(filehash + '\n')


def get_all_files(directory):
    for root, dirs, files in os.walk(directory):
        print(f"Processing subdirectory {root}")
        print_memory_usage()
        for file in files:
            yield os.path.join(root, file)


def update_duplicate_details(filehash, filepaths, output_file):
    with open(output_file, 'a') as f:
        f.write(f"Duplicate file for hash {filehash} (Occurrences: {len(filepaths)}):\n")
        for filepath in filepaths:
            f.write(f"  {filepath}\n")
            f.write(f"  File size: {os.path.getsize(filepath)} bytes\n")
        f.write("\n")
    print(f"{BOLD}{RED}Duplicate found for hash: {filehash} ({len(filepaths)} duplicates){RESET}")
    return sum(os.path.getsize(filepath) for filepath in filepaths)


def process_hash_dict(hashes, total_duplicates_count, duplicates_total_size, output_file):
    for filehash, filepaths in hashes.items():
        if len(filepaths) > 1:
            total_duplicates_count += 1
            duplicates_total_size += update_duplicate_details(filehash, filepaths, output_file)
    return total_duplicates_count, duplicates_total_size


def identify_duplicates(directories, output_file, hash_file_path):
    start_time = time.time()
    duplicates_total_size = 0
    total_duplicates_count = 0

    for directory in directories:
        print(f"Processing directory {directory}")
        dir_start_time = time.time()

        hashes = {}
        file_count = 0

        filepaths = list(get_all_files(directory))
        with Pool(processes=cpu_count()) as pool:
            args = [(filepath, hashes, hash_file_path) for filepath in filepaths]
            results = pool.map(worker, args)
            for filehash, filepath in results:
                if filehash is not None:
                    if filehash in hashes:
                        hashes[filehash].append(filepath)
                    else:
                        hashes[filehash] = [filepath]

            # Check if the dictionary size is above the limit
            if len(hashes) > MAX_DICT_SIZE:
                print(f"{BOLD}{YELLOW}Hash dictionary has reached maximum size, pausing to update log and clear dictionary...{RESET}")
                total_duplicates_count, duplicates_total_size = process_hash_dict(hashes, total_duplicates_count, duplicates_total_size, output_file)
                hashes.clear()

        # Process remaining hashes in the dictionary after scanning all files
        total_duplicates_count, duplicates_total_size = process_hash_dict(hashes, total_duplicates_count, duplicates_total_size, output_file)

        dir_elapsed_time = time.time() - dir_start_time
        print(f"{BOLD}{YELLOW}Finished processing directory {directory} in {dir_elapsed_time:.2f} seconds{RESET}")

    # Print report
    print(f"----- Report -----")
    print(f"Total number of duplicate files: {total_duplicates_count}")
    print(f"Total size of all duplicate files: {duplicates_total_size} bytes")

    end_time = time.time()
    print(f"Script ended at {time.ctime(end_time)}, total elapsed time: {end_time - start_time:.2f} seconds")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide the directories to scan as command-line arguments.")
        sys.exit(1)
    directories = sys.argv[1:]
    output_file = '/Users/ofirozeri/development/playground/duplicate_scanner/duplicates_multi_proc.txt'
    hash_file_path = '/Users/ofirozeri/development/playground/duplicate_scanner/hashes_multi_proc.txt'

    enable_tracemalloc()

    start_time = time.time()
    print(f"Script started at {time.ctime(start_time)}")
    try:
        identify_duplicates(directories, output_file, hash_file_path)
    except KeyboardInterrupt:
        print("Script execution interrupted. Do you want to delete the output files?")
        try:
            os.remove(output_file)
            os.remove(hash_file_path)
            print("Output files deleted successfully.")
        except OSError as e:
            print(f"Error deleting output files: {str(e)}")
    sys.exit(1)
