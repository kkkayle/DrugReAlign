from pymol import cmd

class PDBQTCombiner:
    def __init__(self, receptor_pdbqt_path, ligand_pdbqt_path):
        self.receptor_pdbqt_path = receptor_pdbqt_path
        self.ligand_pdbqt_path = ligand_pdbqt_path

    def convert_pdbqt_to_pdb(self, pdbqt_path, output_pdb_path):
        cmd.load(pdbqt_path)
        cmd.save(output_pdb_path)
        cmd.delete('all')

    def combine_pdb_files(self, receptor_pdb_path, ligand_pdb_path, output_pdb_path):
        cmd.load(receptor_pdb_path, 'receptor')
        cmd.load(ligand_pdb_path, 'ligand')
        cmd.create('combined', 'receptor or ligand')
        cmd.save(output_pdb_path, 'combined')
        cmd.delete('all')

    def combine_pdbqt(self, output_pdb_path):
        receptor_pdb_path = 'receptor.pdb'
        ligand_pdb_path = 'ligand.pdb'

        self.convert_pdbqt_to_pdb(self.receptor_pdbqt_path, receptor_pdb_path)
        self.convert_pdbqt_to_pdb(self.ligand_pdbqt_path, ligand_pdb_path)

        self.combine_pdb_files(receptor_pdb_path, ligand_pdb_path, output_pdb_path)
        #print(f"Combined PDB file saved at: {output_pdb_path}")