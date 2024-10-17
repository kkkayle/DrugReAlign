import os
import argparse
import requests
import json
import re
import threading
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.live import Live
from rich.table import Table
from config.PLIPProcessor import PLIPProcessor
from config.PDBInteractionExtractor import PDBInteractionExtractor
from config.PDBSummaryExtractor import PDBSummaryExtractor
from config.TemplateFiller import TemplateFiller
from config.CompoundConverter import CompoundConverter
from config.PDBConverter import PDBConverter
from config.PDBQTCombiner import PDBQTCombiner
from openai import OpenAI
from config.Docking import Docking
import csv
Finish=False
console = Console()

# Function to download PDB and FASTA files
def download_files(pdb_id, save_root='./data/'):
    pdb_path = f'{save_root}/pdb/{pdb_id}.pdb'
    fasta_path = f'{save_root}/fasta/{pdb_id}.fasta'

    if not os.path.exists(pdb_path):
        pdb_url = f'https://files.rcsb.org/download/{pdb_id}.pdb'
        response = requests.get(pdb_url)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(pdb_path), exist_ok=True)
            with open(pdb_path, 'w') as file:
                file.write(response.text)
        else:
            console.print(f'Failed to retrieve PDB file: {response.status_code}', style="bold red")

    if not os.path.exists(fasta_path):
        fasta_url = f'https://www.rcsb.org/fasta/entry/{pdb_id}'
        response = requests.get(fasta_url)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(fasta_path), exist_ok=True)
            with open(fasta_path, 'w') as file:
                file.write(response.text)
        else:
            console.print(f'Failed to retrieve FASTA file: {response.status_code}', style="bold red")

    return pdb_path, fasta_path

# Function to save formatted data to CSV
def save_data_to_csv(data, file_name,energy=False):
    csv_columns = ['ranking', 'name', 'explanation']
    if energy:
        csv_columns = ['ranking', 'name', 'explanation','energy']
    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

# Function to process the answer file and format it as CSV
def process_answer_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_str = content[json_start:json_end]
        data = json.loads(json_str)
        if 'drug' in data['drugs'][0]['name'] or 'Drug' in data['drugs'][0]['name']:
            raise ValueError("Invalid drug name")
        elif contains_chinese(data['drugs'][0]['name']):
            raise ValueError("Drug name contains Chinese characters")
        if len(data['drugs']) < 5:
            return False, file_path

        return True, data['drugs']
    except Exception as e:
        console.print(f"Error processing file {file_path}: {e}", style="bold red")
        return False, file_path

# Function to check if a string contains Chinese characters
def contains_chinese(s):
    return re.search("[\u4e00-\u9fff]", s)

def main(pdb_id):
    # Define progress bar with tasks
    progress = Progress(
        SpinnerColumn(), 
        TextColumn("{task.description}"), 
        BarColumn(), 
        TextColumn("{task.completed}/{task.total}"), 
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
    )
    
    task_ids = {
        'download': progress.add_task("[#00A6ED]Downloading PDB and FASTA files...", total=2),
        'summary': progress.add_task("[#00A6ED]Fetching PDB summary...", total=1),
        'interaction': progress.add_task("[#00A6ED]Processing spatial interaction data...", total=1),
        'template': progress.add_task("[#00A6ED]Filling question template...", total=1),
        'chatgpt': progress.add_task("[#00A6ED]Interacting with ChatGPT...", total=1),
        'process_answer': progress.add_task("[#00A6ED]Processing ChatGPT answer...", total=1),
        'convert_drug': progress.add_task("[#00A6ED]Converting drug data format...", total=5),
        'convert_pdb': progress.add_task("[#00A6ED]Converting PDB to PDBQT...", total=1),
        'docking': progress.add_task("[#00A6ED]Executing docking and processing results...", total=5)
    }

    log_table = Table.grid()
    log_table.add_column("Log")


    logs = ["", "","", ""]
    def log(message,color= "#f69b7e"):
        # Define the style for log messages
        

        # Update the log message list, keeping only the most recent four messages
        logs.append(message)
        if len(logs) > 4:  # Increase buffer size to 4
            logs.pop(0)
        
        # Rebuild the log_table
        log_table = Table.grid()
        log_table.add_column("Log", style=color)  # Apply the style
        for log_message in logs:
            log_table.add_row(log_message)
        
        # Clear the console and print the progress bar and log table
        console.clear()
        console.print(progress)
        console.print(log_table)





    with Live(console=console, refresh_per_second=10):
        # Download PDB and FASTA files
        pdb_path, fasta_path = download_files(pdb_id)
        progress.update(task_ids['download'], advance=2, completed=2)
        log(f"Downloaded PDB and FASTA files for {pdb_id}")

        # Define paths for other resources
        template_path = './config/template.txt'
        summary_save_path = './data/summary/'
        spatial_information_save_path = './data/spatial_information/'

        # Extract and save summary
        summary_extractor = PDBSummaryExtractor(summary_folder=summary_save_path)
        summary_extractor.fetch_and_save_summary(pdb_id)
        progress.update(task_ids['summary'], advance=1, completed=1)
        log(f"Fetched PDB summary for {pdb_id}")

        # Process and save interaction data
        interaction_extractor = PDBInteractionExtractor(pdb_path=pdb_path, spatial_information_folder=spatial_information_save_path)
        interaction_extractor.process_and_save()
        progress.update(task_ids['interaction'], advance=1, completed=1)
        log(f"Processed spatial interaction data for {pdb_id}")

        # Fill template with extracted data
        filler = TemplateFiller(template_path, summary_save_path, spatial_information_save_path, fasta_path, f'./data/question/')
        filler.process_files(pdb_id)
        progress.update(task_ids['template'], advance=1, completed=1)
        log(f"Filled question template for {pdb_id}")
        
        question = open(f'./data/question/{pdb_id}.txt').read().replace("\n", " ")
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": question}
            ]
        )
        answer = completion.choices[0].message.content
        with open(f'./data/answer/{pdb_id}.txt', 'w', encoding='utf-8') as f:
            f.write(answer)
        progress.update(task_ids['chatgpt'], advance=1, completed=1)
        log(f"Interacted with ChatGPT for {pdb_id}")
        
        # Process the generated answer file
        answer_file_path = f'./data/answer/{pdb_id}.txt'
        is_correct, result = process_answer_file(answer_file_path)
        if is_correct:
            csv_file_name = f'./data/answer/{pdb_id}.csv'
            save_data_to_csv(result, csv_file_name)
            progress.update(task_ids['process_answer'], advance=1, completed=1)
            log(f"Processed ChatGPT answer for {pdb_id} and saved to CSV")
        else:
            log(f"Failed to process answer file {answer_file_path}")
            main(pdb_id)  # Re-execute the main function
            return

        converter = CompoundConverter(output_dir='./data/drug_pdbqt')
        for i in result:
            drugname = i['name']
            sign = converter.process(drugname)
            if sign:
                log(f"Converted drug {drugname} to PDBQT format",color="#f69b7e")
            else:
                log(f"Failed to convert drug {drugname} to PDBQT format",color="#f69b7e")
            progress.update(task_ids['convert_drug'], advance=1)

        converter = PDBConverter(pdb_path=f'./data/pdb/{pdb_id}.pdb', pdbqt_path=f'./data/rec_pdbqt/{pdb_id}.pdbqt')
        pdbqt_file = converter.convert_pdb_to_pdbqt()
        log(f"Converted PDB to PDBQT: {pdbqt_file}",color="#f69b7e")
        progress.update(task_ids['convert_pdb'], advance=1, completed=1)

        for i in range(len(result)):
            drugname = result[i]['name']
            docking_instance = Docking(protein=pdb_id, drug=drugname, exhaustiveness=1)
            score = docking_instance.execute_docking()
            progress.update(task_ids['docking'], advance=1)
            result[i]['energy'] = score
            log(f'Docking {pdb_id}_{drugname} ENERGY: {score}(kcal/mol)')
            if float(score) < 0:
                combiner = PDBQTCombiner(f'./data/rec_pdbqt/{pdb_id}.pdbqt', f'./data/dock_result/{pdb_id}_{drugname}.pdbqt')
                combiner.combine_pdbqt(f'./data/combined_result/{pdb_id}_{drugname}.pdb')
                # Initialize and run the PLIP processor
                plip_processor = PLIPProcessor(pdb_path=f'./data/combined_result/{pdb_id}_{drugname}.pdb', output_dir='./result/visualize')
                plip_processor.process()
        save_data_to_csv(result, f'./result/csv/{pdb_id}.csv',energy=True)
        global Finish
        Finish=True
        log(f"FINISH!")

def run_thread(pdb_id):
    while not Finish:
        t = threading.Thread(target=main, args=(pdb_id,))
        t.start()
        t.join()
        if not Finish:
            console.log("Thread terminated unexpectedly. Restarting...",style="Bold green")
            import time
            time.sleep(2)
        else:
            console.log("Process completed successfully, no restart needed.",style="Bold green")


if __name__ == "__main__":
    # Configure OpenAI API client
    client = OpenAI(api_key="",base_url="")
    parser = argparse.ArgumentParser(description="Run DrugReAlign with PDB ID")
    parser.add_argument('--pdb_id', help="Provide the PDB ID to process")

    args = parser.parse_args()

    # Check if PDB ID is provided via command-line argument, otherwise use input()
    if args.pdb_id:
        pdb_id = args.pdb_id
    else:
        # Prompt user to input the PDB ID if not provided via command line
        # pdb_id = input("Please enter the PDB ID: ")
        pass
    # Execute the main function
    run_thread('1C8K')
