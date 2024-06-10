import os
import subprocess
import shutil

class PLIPProcessor:
    def __init__(self, pdb_path, output_dir='./data/visualize'):
        self.pdb_path = pdb_path
        self.output_dir = output_dir
        self.temp_dir = './temp_plip_files'
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        
    def run_plip(self):
        # Change to the temporary directory
        os.chdir(self.temp_dir)
        
        # Execute the PLIP command
        command = f'plip -f ../{self.pdb_path} -yv'
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chdir('../')
        # Find the generated PSE file
        pse_file = None
        for file in os.listdir(self.temp_dir):
            if file.endswith('.pse'):
                pse_file = file
                break
        
        if pse_file:
            # Move the PSE file to the output directory
            shutil.move(os.path.join(self.temp_dir,pse_file), os.path.join(self.output_dir, pse_file))
            #print(f'Moved PSE file to {self.output_dir}/{pse_file}')
        else:
            print('PSE file not found.')

        # Clean up the temporary directory
        self.cleanup_temp_files()

    def cleanup_temp_files(self):
        # Remove all files in the temporary directory
        for file in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, file)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    def process(self):
        self.run_plip()

if __name__ == "__main__":
    # Example usage
    pdb_id = input("Please enter the PDB ID: ")
    pdb_path = f'./data/pdb/{pdb_id}.pdb'
    
    # Ensure the PDB file exists
    if not os.path.exists(pdb_path):
        print(f'PDB file {pdb_path} does not exist.')
        exit(1)
    
    # Initialize and run the PLIP processor
    plip_processor = PLIPProcessor(pdb_path=pdb_path)
    plip_processor.process()
