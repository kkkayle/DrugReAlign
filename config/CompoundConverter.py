import pubchempy as pcp
import os
import multiprocessing
from rdkit import Chem
from rdkit.Chem import AllChem
from openbabel import pybel
import logging

class CompoundConverter:
    def __init__(self, output_dir='./lig_pdbqt'):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        logging.basicConfig(filename='conversion_errors.log', level=logging.ERROR)

    def get_smiles(self, name):
        try:
            compound = pcp.get_compounds(name, 'name')
            return compound[0].isomeric_smiles if compound else 'Not Found'
        except Exception as e:
            logging.error(f"Error processing {name}: {e}")
            return 'Error'

    def smiles_to_3D_worker(self, smiles, output_path):
        try:
            mol = Chem.MolFromSmiles(smiles)
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, AllChem.ETKDG())
            AllChem.UFFOptimizeMolecule(mol)
            mol_block = Chem.MolToMolBlock(mol)
            ob_conversion = pybel.ob.OBConversion()
            ob_conversion.SetInAndOutFormats("sdf", "pdbqt")
            ob_mol = pybel.readstring("sdf", mol_block)
            ob_mol.addh()
            ob_mol.make3D(forcefield="mmff94", steps=50)  # Adjust forcefield and steps to avoid crashes
            ob_conversion.WriteFile(ob_mol.OBMol, output_path)
            return True
        except Exception as e:
            logging.error(f"Error converting SMILES to PDBQT: {e}")
            return False

    def smiles_to_3D(self, smiles, output_path):
        try:
            process = multiprocessing.Process(target=self.smiles_to_3D_worker, args=(smiles, output_path))
            process.start()
            process.join()
            if process.exitcode != 0:
                raise RuntimeError("Subprocess ended with a non-zero exit code")
                return False
            return True
        except Exception as e:
            logging.error(f"Error converting SMILES to PDBQT in subprocess: {e}")
            return False
    def process(self, compound_name):
        if '/' in compound_name:
            compound_name = compound_name.replace('/', '_')
        smiles = self.get_smiles(compound_name)
        if smiles == 'Not Found' or smiles == 'Error':
            print(f"SMILES not found for {compound_name}")
            return
        output_path = os.path.join(self.output_dir, f"{compound_name}.pdbqt")
        sign=True
        if not os.path.exists(output_path):
            sign=self.smiles_to_3D(smiles, output_path)
        return sign

    def pdb_to_pdbqt(self, pdb_path):
        try:
            file_name = os.path.basename(pdb_path)
            base_name = os.path.splitext(file_name)[0]
            output_path = os.path.join(self.output_dir, f"{base_name}.pdbqt")
            ob_conversion = pybel.ob.OBConversion()
            ob_conversion.SetInAndOutFormats("pdb", "pdbqt")
            ob_mol = next(pybel.readfile("pdb", pdb_path))
            ob_mol.addh()
            ob_mol.make3D(forcefield="mmff94", steps=50)
            ob_conversion.WriteFile(ob_mol.OBMol, output_path)
            print(f"Converted {pdb_path} to {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"Error converting PDB to PDBQT: {e}")
            return False