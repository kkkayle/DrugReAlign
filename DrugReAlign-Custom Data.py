# Import necessary libraries
import os
import requests
import yaml  # PyYAML library for handling YAML files
import re
import json
import threading
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
from Bio.PDB import PDBParser, is_aa, Polypeptide, PDBIO

# Set global flag
Finish = False

# Define important file paths
template_path = './config/template.txt'
summary_save_path = './data/summary/'
spatial_information_save_path = './data/spatial_information/'

# Function to load YAML configuration file
def load_config(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Function to extract amino acid sequences from PDB file
def get_amino_acid_sequence(pdb_path):
    """
    Extract amino acid sequences from a PDB file (represented in one-letter code).
    Filters out small molecules, water, and ions.
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('PDB_structure', pdb_path)
    sequences = []

    for model in structure:
        for chain in model:
            ppb = Polypeptide.PPBuilder()
            for poly_index in ppb.build_peptides(chain):
                sequence = poly_index.get_sequence()
                if sequence:
                    sequences.append(str(sequence))

    return sequences

# Function to search for the best matching PDB structure using a protein sequence
def search_pdb(sequence):
    url = "https://search.rcsb.org/rcsbsearch/v2/query?json="
    query = {
        "query": {
            "type": "terminal",
            "service": "sequence",
            "parameters": {
                "evalue_cutoff": 1,
                "identity_cutoff": 0.9,
                "target": "pdb_protein_sequence",
                "value": sequence
            }
        },
        "request_options": {
            "scoring_strategy": "sequence"
        },
        "return_type": "entry"
    }

    response = requests.post(url, json=query)

    if response.status_code == 200:
        data = response.json()
        if "result_set" in data and data["result_set"]:
            return data["result_set"][0]["identifier"]
        else:
            return None
    else:
        print(f"Error: {response.status_code}")
        return None

# Find the best matching PDB structure from the PDB file
def find_best_pdb_structure(pdb_path):
    """
    Extract the amino acid sequence from the PDB file and find the most similar PDB structure by sequence.
    """
    sequences = get_amino_acid_sequence(pdb_path)

    if not sequences:
        print("No amino acid sequences found.")
        return None
    sequence = sequences[0]
    best_pdb = search_pdb(sequence)

    if best_pdb:
        print(f"The most similar PDB structure is: {best_pdb}")
    else:
        print("No similar PDB structure found.")

    return best_pdb, sequence

# Function to download PDB and FASTA files if not already present
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
            print(f'Failed to retrieve PDB file: {response.status_code}')

    if not os.path.exists(fasta_path):
        fasta_url = f'https://www.rcsb.org/fasta/entry/{pdb_id}'
        response = requests.get(fasta_url)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(fasta_path), exist_ok=True)
            with open(fasta_path, 'w') as file:
                file.write(response.text)
        else:
            print(f'Failed to retrieve FASTA file: {response.status_code}')

    return pdb_path, fasta_path

# Function to save data to CSV
def save_data_to_csv(data, file_name, energy=False):
    csv_columns = ['ranking', 'name', 'explanation']
    if energy:
        csv_columns.append('energy')
    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

# Function to process an answer file and validate its content
def process_answer_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_str = content[json_start:json_end]
        data = json.loads(json_str)
        
        # Validate drug names
        if 'drug' in data['drugs'][0]['name'] or contains_chinese(data['drugs'][0]['name']):
            raise ValueError("Invalid drug name")

        if len(data['drugs']) < 5:
            return False, file_path

        return True, data['drugs']
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False, file_path

# Function to check if a string contains Chinese characters
def contains_chinese(s):
    return re.search("[\u4e00-\u9fff]", s)

# Extract ligands from PDB and optionally split into individual files
def get_ligand_from_pdb(pdb, output_dir, split=True):
    parser = PDBParser(QUIET=True)
    pdb_path = f'./data/pdb/{pdb}.pdb'
    structure = parser.get_structure('PDB_structure', pdb_path)
    
    # List of common metal and ion names to exclude
    ions_metals = {'NA', 'K', 'MG', 'CA', 'ZN', 'FE', 'MN', 'CU', 'CO', 'NI', 'CL', 'SO4', 'PO4', 'IOD', 'BR', 'F', 'I'}
    ligands = []
    
    for model in structure:
        for chain in model:
            for residue in chain:
                # Exclude standard amino acids, water, ions, and metals
                if not is_aa(residue, standard=True) and residue.id[0] != 'W' and residue.resname not in ions_metals:
                    ligands.append(residue)
                    if split:
                        lig_path = save_ligand_as_pdb(residue, output_dir)
                        return lig_path
                    else:
                        return True
    return False

# Function to save ligand structure as a PDB file
def save_ligand_as_pdb(ligand, output_dir):
    io = PDBIO()
    io.set_structure(ligand)
    ligand_name = f"{ligand.resname}_{ligand.id[1]}_{ligand.get_parent().id}.pdb"
    io.save(f"{output_dir}/{ligand_name}")
    return f"{output_dir}/{ligand_name}"

# Function to get summary information from config and print it
def get_summary_info_from_config(config):
    summary_info = config["manual_upload"]["summary_info"]
    summary_string = "\n ".join([f"{key}: {value}" for key, value in summary_info.items()])
    print(f"Using user-provided summary: {summary_string}")
    return summary_string

# Main function that executes the core workflow
def main(config):
    mode = config["mode"]
    pdb_path = None

    if mode == "manual_upload":
        # Handling manual PDB uploads
        pdb_path = config["manual_upload"]["pdb_file_path"]
        file_name = os.path.splitext(os.path.basename(pdb_path))[0]
        print(f"Using manually uploaded PDB file: {file_name}")

        sequence = get_amino_acid_sequence(pdb_path)
        save_path = f"./data/fasta/{os.path.splitext(os.path.basename(pdb_path))[0]}.fasta"
        with open(save_path, "w") as f:
            f.write(f"> {os.path.basename(save_path)}\n{sequence}")

        if config["manual_upload"]["use_summary"]:
            summary_info = get_summary_info_from_config(config)
            output_path = f'./data/summary/{file_name}.txt'
            # Write summary info to a text file
            with open(output_path, 'w') as file:
                file.write(str(summary_info))
        else:
            similar_pdb = find_best_pdb_structure(pdb_path)
            summary_extractor = PDBSummaryExtractor(summary_folder='./data/summary/')
            summary_extractor.fetch_and_save_summary(similar_pdb)

        if get_ligand_from_pdb(file_name, './data/temp/', split=False) == False:
            similar_pdb = find_best_pdb_structure(pdb_path)
            download_files(similar_pdb)
            lig_path = get_ligand_from_pdb(file_name, './data/temp/', split=True)
            converter = CompoundConverter(output_dir='./data/drug_pdbqt')
            lig_path = converter.pdb_to_pdbqt(lig_path)
            converter = PDBConverter(pdb_path=f'./data/pdb/{file_name}.pdb', pdbqt_path=f'./data/rec_pdbqt/{file_name}.pdbqt')
            rec_path = converter.convert_pdb_to_pdbqt()
            drug_name = os.path.splitext(lig_path)[0]
            docking_instance = Docking(protein=file_name, drug=drug_name, exhaustiveness=8)
            score = docking_instance.execute_docking()
            print(f'score: {score}')

            if float(score) < 0:
                combiner = PDBQTCombiner(rec_path, f'./data/dock_result/{file_name}_{drug_name}.pdbqt')
                combiner.combine_pdbqt(f'./data/pdb/{file_name}.pdb')
                interaction_path = f'./data/pdb/{file_name}.pdb'
        else:
            interaction_path = pdb_path

        # Extract interaction data and save it
        interaction_extractor = PDBInteractionExtractor(pdb_path=interaction_path,
                                                        spatial_information_folder=spatial_information_save_path)
        interaction_extractor.process_and_save()

        # Fill template with the gathered information
        filler = TemplateFiller(template_path, summary_save_path, spatial_information_save_path, './data/fasta/',
                                f'./data/question/')
        filler.process_files(file_name)

        # Use OpenAI API to generate an answer based on the processed data
        question = open(f'./data/question/{file_name}.txt').read().replace("\n", " ")
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": question}
            ]
        )
        answer = completion.choices[0].message.content
        with open(f'./data/answer/{file_name}.txt', 'w', encoding='utf-8') as f:
            f.write(answer)

        # Process the generated answer file
        answer_file_path = f'./data/answer/{file_name}.txt'
        is_correct, result = process_answer_file(answer_file_path)
        csv_file_name = f'./data/answer/{file_name}.csv'
        save_data_to_csv(result, csv_file_name)

        # Further process the data for docking and interaction analysis
        converter = CompoundConverter(output_dir='./data/drug_pdbqt')
        for i in result:
            drugname = i['name']
            sign = converter.process(drugname)

        converter = PDBConverter(pdb_path=pdb_path, pdbqt_path=f'./data/rec_pdbqt/{file_name}.pdbqt')
        pdbqt_file = converter.convert_pdb_to_pdbqt()

        for i in range(len(result)):
            drugname = result[i]['name']
            docking_instance = Docking(protein=file_name, drug=drugname, exhaustiveness=1)
            score = docking_instance.execute_docking()

            result[i]['energy'] = score

            if float(score) < 0:
                combiner = PDBQTCombiner(f'./data/rec_pdbqt/{file_name}.pdbqt',
                                         f'./data/dock_result/{file_name}_{drugname}.pdbqt')
                combiner.combine_pdbqt(f'./data/combined_result/{file_name}_{drugname}.pdb')
                # Initialize and run the PLIP processor
                plip_processor = PLIPProcessor(pdb_path=f'./data/combined_result/{file_name}_{drugname}.pdb',
                                               output_dir='./result/visualize')
                plip_processor.process()

        save_data_to_csv(result, f'./result/csv/{file_name}.csv', energy=True)
        global Finish
        Finish = True

    elif mode == "sequence_search":
        # Handling PDB search based on sequence
        sequence = config["sequence_search"]["query_sequence"]
        print(f"Using sequence search for: {sequence}")
        pdb_id = find_best_pdb_structure(sequence)
        pdb_path, _ = download_files(pdb_id)
        file_name = sequence[:4]
        if config["sequence_search"]["use_summary"]:
            summary_info = get_summary_info_from_config(config)
            output_path = f'./data/summary/{file_name}.txt'
            # Write summary info to a text file
            with open(output_path, 'w') as file:
                file.write(str(summary_info))
        else:
            summary_extractor = PDBSummaryExtractor(summary_folder='./data/summary/')
            summary_extractor.fetch_and_save_summary(pdb_id)
            print(f"Fetched PDB summary for {pdb_id}")
        interaction_path = pdb_path

        # Extract interaction data
        interaction_extractor = PDBInteractionExtractor(pdb_path=interaction_path,
                                                        spatial_information_folder=spatial_information_save_path)
        interaction_extractor.process_and_save()

        filler = TemplateFiller(template_path, summary_save_path, spatial_information_save_path, './data/fasta/',
                                f'./data/question/')
        filler.process_files(file_name)

        question = open(f'./data/question/{file_name}.txt').read().replace("\n", " ")
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": question}
            ]
        )
        answer = completion.choices[0].message.content
        with open(f'./data/answer/{file_name}.txt', 'w', encoding='utf-8') as f:
            f.write(answer)

        # Process the generated answer file
        answer_file_path = f'./data/answer/{file_name}.txt'
        is_correct, result = process_answer_file(answer_file_path)
        csv_file_name = f'./data/answer/{file_name}.csv'
        save_data_to_csv(result, csv_file_name)

        # Further process the data for docking and interaction analysis
        converter = CompoundConverter(output_dir='./data/drug_pdbqt')
        for i in result:
            drugname = i['name']
            sign = converter.process(drugname)

        converter = PDBConverter(pdb_path=pdb_path, pdbqt_path=f'./data/rec_pdbqt/{file_name}.pdbqt')
        pdbqt_file = converter.convert_pdb_to_pdbqt()

        for i in range(len(result)):
            drugname = result[i]['name']
            docking_instance = Docking(protein=file_name, drug=drugname, exhaustiveness=1)
            score = docking_instance.execute_docking()

            result[i]['energy'] = score

            if float(score) < 0:
                combiner = PDBQTCombiner(f'./data/rec_pdbqt/{file_name}.pdbqt',
                                         f'./data/dock_result/{file_name}_{drugname}.pdbqt')
                combiner.combine_pdbqt(f'./data/combined_result/{file_name}_{drugname}.pdb')
                # Initialize and run the PLIP processor
                plip_processor = PLIPProcessor(pdb_path=f'./data/combined_result/{file_name}_{drugname}.pdb',
                                               output_dir='./result/visualize')
                plip_processor.process()

        save_data_to_csv(result, f'./result/csv/{file_name}.csv', energy=True)
        global Finish
        Finish = True

    else:
        raise ValueError(f"Unknown mode: {mode}")

# Function to run the process in a separate thread and restart if necessary
def run_thread(config):
    while not Finish:
        t = threading.Thread(target=main, args=(config,))
        t.start()
        t.join()
        if not Finish:
            print("Thread terminated unexpectedly. Restarting...")
            import time
            time.sleep(2)
        else:
            print("Process completed successfully, no restart needed.")

# Main execution block
if __name__ == "__main__":
    config_file = 'config.yaml'
    config = load_config(config_file)

    # Configure OpenAI API client
    client = OpenAI(api_key="", base_url="")

    # Execute the main function with configuration
    run_thread(config)
