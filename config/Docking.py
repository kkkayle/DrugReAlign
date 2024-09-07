import numpy as np
import os
from vina import Vina
def extract_first_energy_from_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if "REMARK VINA RESULT:" in line:
                # 假设能量值紧跟在'REMARK VINA RESULT:'之后
                energy = float(line.split()[3])
                return energy
    return None
class Docking:
    def __init__(self, protein, drug, exhaustiveness=64):
        self.protein = protein
        self.drug = drug
        self.exhaustiveness = exhaustiveness
        self.drug_path = f'./data/drug_pdbqt/{self.drug}.pdbqt'
        self.protein_path = f'./data/rec_pdbqt/{self.protein}.pdbqt'
        self.output_path = f'./data/dock_result/{self.protein}_{self.drug}.pdbqt'

    def calculate_docking_box(self, receptor_pdb_path):
        with open(receptor_pdb_path, 'r') as file:
            lines = file.readlines()

        coords = []
        for line in lines:
            if line.startswith('ATOM') or line.startswith('HETATM'):
                x = float(line[30:38].strip())
                y = float(line[38:46].strip())
                z = float(line[46:54].strip())
                coords.append((x, y, z))

        coords = np.array(coords)
        min_coords = coords.min(axis=0)
        max_coords = coords.max(axis=0)

        center = (min_coords + max_coords) / 2
        size = max_coords - min_coords

        return center, size

    def run_dock(self, center, size):
        v = Vina()
        v.set_receptor(rigid_pdbqt_filename=self.protein_path)
        v.set_ligand_from_file(self.drug_path)
        v.compute_vina_maps(center=center, box_size=size)
        v.dock(exhaustiveness=self.exhaustiveness)
        v.write_poses(pdbqt_filename=self.output_path)
        score=v.energies()[0][0]
        return score
    def execute_docking(self):
        if not os.path.exists(self.output_path):
            if os.path.exists(self.drug_path):
                center, size = self.calculate_docking_box(self.protein_path)
                try:
                    score=self.run_dock(center=center, size=size)
                    return score
                except Exception as e:
                    score=-1
                    print(f"Error during docking: {e}")
                    return score
        else:
            score=extract_first_energy_from_file(self.output_path)
            return score

