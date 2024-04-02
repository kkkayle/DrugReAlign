import numpy as np
import pandas as pd
import os
import re
from plip.structure.preparation import PDBComplex
from plip.exchange.report import BindingSiteReport

class PDBInteractionExtractor:
    def __init__(self, pdb_path, spatial_information_folder='./3D'):
        self.pdb_path = pdb_path
        self.spatial_information_folder = spatial_information_folder
        if not os.path.exists(self.spatial_information_folder):
            os.makedirs(self.spatial_information_folder)
        self.attri_dict = {
            'hydrophobic': ['RESTYPE', 'RESCHAIN', 'RESCHAIN_LIG', 'DIST', 'LIGCOO', 'PROTCOO'],
            'hbond': ['RESTYPE', 'RESCHAIN', 'RESTYPE_LIG', 'PROTCOO', 'LIGCOO', 'DIST_H-A', 'DIST_D-A', 'DON_ANGLE', 'DONORTYPE', 'ACCEPTORTYPE'],
            'pistacking': ['RESTYPE', 'RESCHAIN', 'RESTYPE_LIG', 'CENTDIST', 'ANGLE', 'OFFSET', 'PROTCOO', 'LIGCOO']
        }

    @staticmethod
    def remove_consecutive_spaces(s):
        return re.sub(r' +', ' ', s)

    def retrieve_plip_interactions(self):
        protlig = PDBComplex()
        protlig.load_pdb(self.pdb_path)
        for ligand in protlig.ligands:
            protlig.characterize_complex(ligand)
        sites = {}
        for key, site in sorted(protlig.interaction_sets.items()):
            binding_site = BindingSiteReport(site)
            keys = ("hydrophobic", "hbond", "pistacking")
            interactions = {k: [getattr(binding_site, f"{k}_features")] + getattr(binding_site, f"{k}_info") for k in keys}
            sites[key] = interactions
        return sites

    def create_df_from_binding_site(self, selected_site_interactions, interaction_type="hbond"):
        df = pd.DataFrame.from_records(selected_site_interactions[interaction_type][1:], columns=selected_site_interactions[interaction_type][0])
        return df

    def process_and_save(self):
        interactions_by_site = self.retrieve_plip_interactions()
        result_dict = {}
        for interaction_type in ["hydrophobic", "hbond", "pistacking"]:
            for key in interactions_by_site.keys():
                df = self.create_df_from_binding_site(interactions_by_site[key], interaction_type)
                if interaction_type not in result_dict:
                    result_dict[interaction_type] = df
                else:
                    result_dict[interaction_type] = pd.concat([result_dict[interaction_type], df])

        spatial_information_filename = os.path.join(self.spatial_information_folder, os.path.basename(self.pdb_path).replace('.pdb', '.txt'))
        with open(spatial_information_filename, 'w', encoding='utf-8') as f:
            for key, df in result_dict.items():
                if len(df) == 0:
                    continue
                df = df[self.attri_dict[key]]
                f.write(self.remove_consecutive_spaces(f'"""{key}""":\n{df.to_string(index=False)}\n'))

if __name__ == '__main__':
    pdb_path = 'path_to_your_pdb_file.pdb'  # Update this with your actual PDB file path
    extractor = PDBInteractionExtractor(pdb_path)
    extractor.process_and_save()
