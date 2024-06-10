import requests
from bs4 import BeautifulSoup
import os

class PDBSummaryExtractor:
    def __init__(self, summary_folder='./summary'):
        self.summary_folder = summary_folder
        if not os.path.exists(self.summary_folder):
            os.makedirs(self.summary_folder)

    def fetch_and_save_summary(self, pdb_id):
        summary_path = os.path.join(self.summary_folder, f'{pdb_id}.txt')
        if not os.path.exists(summary_path):
            url = f'https://www.rcsb.org/structure/{pdb_id}'
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                html_ids = {
                    'PDB ID': 'structureID',
                    'Title': 'structureTitle',
                    'Classification': 'header_classification',
                    'Organism(s)': 'header_organism',
                    'Expression System': 'header_expression-system'
                }

                result = {}
                for key, item_id in html_ids.items():
                    info_element = soup.find(id=item_id)
                    if info_element:
                        result[key] = info_element.text.strip()
                    else:
                        result[key] = "Not found"

                with open(summary_path, 'w') as file:
                    for key, value in result.items():
                        file.write(f'{key}: {value}\n')

                #print(f'Summary saved for {pdb_id}:', result)
            else:
                print(f'Failed to fetch data for {pdb_id}. HTTP status code: {response.status_code}')
        else:
            pass
            #print(f'Summary already exists for {pdb_id}.')

# Example of how to use the class for a single PDB file
if __name__ == '__main__':
    pdb_id = '4HHB'  # Example PDB ID
    extractor = PDBSummaryExtractor()
    extractor.fetch_and_save_summary(pdb_id)
