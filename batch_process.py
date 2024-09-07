import os
import csv
import subprocess
from concurrent.futures import ThreadPoolExecutor
import time
# Function to run DrugReAlign.py for each PDB entry
def run_drugrealign(pdb_name):
    try:
        # Run the DrugReAlign.py script with the PDB name as an argument
        subprocess.run(['python', 'DrugReAlign.py', '--pdb_id' ,pdb_name], check=True)
        print(f"Successfully processed {pdb_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {pdb_name}: {e}")

# Function to run DrugReAlign-Custom Data.py for each config file
def run_custom_data(config_file):
    try:
        # Run the DrugReAlign-Custom Data.py script with the config file as an argument
        subprocess.run(['python', 'DrugReAlign-Custom Data.py', config_file], check=True)
        print(f"Successfully processed {config_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {config_file}: {e}")

# Function to process a CSV file and run DrugReAlign.py in parallel
def process_drugrealign_csv(csv_file, num_threads=4):
    pdb_list = []
    # Read the CSV file to extract PDB names
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            pdb_list.append(row[0])  # Assume the first column contains PDB names

    # Run DrugReAlign.py using multithreading
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(run_drugrealign, pdb_list)

# Function to process a folder containing config files and run DrugReAlign-Custom Data.py in parallel
def process_custom_data_folder(config_folder, num_threads=4):
    # List all .config files in the specified folder
    config_files = [os.path.join(config_folder, f) for f in os.listdir(config_folder) if f.endswith('.config')]
    
    # Run DrugReAlign-Custom Data.py using multithreading
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(run_custom_data, config_files)

# Main function to handle command-line arguments and choose the appropriate task

# Main function to handle command-line arguments and choose the appropriate task
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch process DrugReAlign or DrugReAlign-Custom Data")
    parser.add_argument('--mode', default='Normal',choices=['Normal', 'Custom'],
                        help="Select mode: 'DrugReAlign' for CSV input, 'Custom' for config folder input")
    parser.add_argument('--csv', default='./batch_input/DrugReAlign/input.csv', help="CSV file for DrugReAlign.py")
    parser.add_argument('--config_folder',default='./batch_input/DrugReAlign-Custom Data', help="Folder containing config files for DrugReAlign-Custom Data.py")
    parser.add_argument('--threads', type=int, default=12, help="Number of threads to use")

    args = parser.parse_args()

    # Handle DrugReAlign mode, which processes CSV input
    if args.mode == 'Normal':
        if args.csv:
            # Start the timer
            start_time = time.time()
            
            process_drugrealign_csv(args.csv, args.threads)
            
            # End the timer and print elapsed time
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"DrugReAlign-Normal mode completed in {elapsed_time:.2f} seconds.")
        else:
            print("Please provide a CSV file for DrugReAlign-Normal mode.")
    
    # Handle Custom mode, which processes a folder of config files and times the execution
    elif args.mode == 'Custom':
        if args.config_folder:
            # Start the timer
            start_time = time.time()
            
            process_custom_data_folder(args.config_folder, args.threads)
            
            # End the timer and print elapsed time
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"DrugReAlign-Custom Data mode completed in {elapsed_time:.2f} seconds.")
        else:
            print("Please provide a config folder for DrugReAlign-Custom Data mode.")
