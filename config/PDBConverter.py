import os
import subprocess
from Bio import PDB

# Please replace the following path
MGLTOOLS_PYTHON = "/home/wjh/autodocktools/mgltools_x86_64Linux2_1.5.6/bin/MGLpython2.5"
PREPARE_RECEPTOR_SCRIPT = "/home/wjh/autodocktools/mgltools_x86_64Linux2_1.5.6/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py"


class PDBConverter:
    def __init__(self, pdbqt_path, pdb_path):
        self.pdbqt_path = pdbqt_path
        self.pdb_file = pdb_path

    class NonHetSelect(PDB.Select):
        def accept_residue(self, residue):
            return residue.id[0] == " "

    def remove_ligands_and_waters(self, pdb_filename, output_filename):
        parser = PDB.PDBParser()
        structure = parser.get_structure("structure", pdb_filename)

        io = PDB.PDBIO()
        io.set_structure(structure)
        io.save(output_filename, self.NonHetSelect())

    def convert_pdb_to_pdbqt(self):
        pdbqt_file = self.pdbqt_path
        if os.path.exists(pdbqt_file):
            return pdbqt_file

        temp_pdb_path = self.pdb_file.replace('.pdb', '_temp.pdb')
        self.remove_ligands_and_waters(self.pdb_file, temp_pdb_path)

        subprocess.run([MGLTOOLS_PYTHON,
                        "-c",
                        f"import sys; sys.path.append('{os.path.dirname(PREPARE_RECEPTOR_SCRIPT)}'); exec(open('{PREPARE_RECEPTOR_SCRIPT}').read())",
                        '-r', temp_pdb_path,
                        '-o', pdbqt_file])

        os.remove(temp_pdb_path)

        return pdbqt_file


if __name__ == '__main__':
    for pdb_id in [i for i in os.listdir('./pdb') if i.endswith('pdb')]:
        converter = PDBConverter(pdb_path=f'./pdb/{pdb_id}', pdbqt_path=f'./pdb/{pdb_id}qt')
        pdbqt_file = converter.convert_pdb_to_pdbqt()
