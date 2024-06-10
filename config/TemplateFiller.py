import os

class TemplateFiller:
    def __init__(self, template_path, summary_folder_path, atom_folder_path, sequence_folder_path, output_folder_path):
        self.template_path = template_path
        self.summary_folder_path = summary_folder_path
        self.atom_folder_path = atom_folder_path
        self.sequence_folder_path = sequence_folder_path
        self.output_folder_path = output_folder_path

        if not os.path.exists(self.output_folder_path):
            os.makedirs(self.output_folder_path)

    def fill_template(self, file_base_name):
        with open(self.template_path, 'r', encoding='utf-8') as file:
            template = file.read()

        summary_path = os.path.join(self.summary_folder_path, file_base_name + '.txt')
        atom_path = os.path.join(self.atom_folder_path, file_base_name + '.txt')
        sequence_path = os.path.join(self.sequence_folder_path, file_base_name + '.fasta')

        summary, atom, sequence = "", "", ""

        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as temp:
                summary = temp.read()
        if os.path.exists(atom_path):
            with open(atom_path, 'r', encoding='utf-8') as temp:
                atom = temp.read()
        if os.path.exists(sequence_path):
            with open(sequence_path, 'r', encoding='utf-8') as temp:
                sequence = temp.read()

        filled_template = template.replace('__fill sum info__', summary)
        filled_template = filled_template.replace('__fill seq info__', sequence)
        filled_template = filled_template.replace('__fill pdb info__', atom)

        save_path = os.path.join(self.output_folder_path, file_base_name + '.txt')

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(filled_template)

    def process_files(self, pdb_id):
        
        self.fill_template(pdb_id)
        #print(f"Processed: {pdb_id}")

# Example of how to use the class
if __name__ == '__main__':
    template_path = 'path_to_your_template.txt'  # Update this path
    summary_folder_path = 'path_to_your_summary_folder'
    atom_folder_path = 'path_to_your_atom_folder'
    sequence_folder_path = 'path_to_your_sequence_folder'
    output_folder_path = 'path_to_your_output_folder'
    
    filler = TemplateFiller(template_path, summary_folder_path, atom_folder_path, sequence_folder_path, output_folder_path)
    
    # Suppose your file base names are something like '1A2B', '2B3C', etc.
    file_list = ['1A2B', '2B3C']  # Update this list with actual base names of your files
    filler.process_files(file_list)
