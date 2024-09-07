
# DrugReAlign

<p align="center">
  <img src="https://github.com/kkkayle/DrugReAlign/blob/master/DrugReAlign.png" width="400">
</p>

This guide outlines the process for utilizing your own data in drug repositioning projects. Follow the steps below to set up your environment and run analyses.

## System Requirements
**Note**: If you need to automate molecular docking, you need to use a Linux system (or manually configure the Vina path on other systems).

Before you begin, ensure your system meets the following requirements:

- **Python Version:** 3.10.13
- **Required Libraries:**
  - numpy==1.26.4
  - pandas==2.2.2
  - plip==2.3.0
  - beautifulsoup4==4.12.3
  - requests==2.32.2
  - openai==1.30.2
  - rdkit==2023.9.6
  - pubchempy==1.0.4
  - vina==1.2.5 (Linux)
  - biopython==1.83
  - rich==13.7.1
  - openbabel==3.1.1
  - pymol-open-source==3.0.0

- **MGLTOOLS:** No specific version requirements.

## Setup Instructions

1. Ensure that the required libraries are installed in your Python environment.
2. Fill in the API key and change the model (if necessary) in `DrugReAlign.py`.
3. Provide the MGLTOOLS path in `config/PDBConverter.py`.
4. Run `DrugReAlign.py` to perform the analysis.
5. The results will be saved in the `result` directory for further review.

## Obtaining PDB Files

If you do not have a PDB file for your protein of interest, you can obtain one from several online resources, including:

- **AlphaFold**: AlphaFold is a powerful tool that predicts 3D protein structures. You can use it to generate PDB files for proteins of interest. [AlphaFold Protein Structure Database](https://alphafold.ebi.ac.uk/)

- **RCSB Protein Data Bank (PDB)**: You can search and download experimental PDB structures from the RCSB Protein Data Bank. [RCSB PDB](https://www.rcsb.org/)

Once you have the PDB file, you can manually upload it to the appropriate directory for analysis.

### Handling Missing Ligands in Manual Upload Mode

In the **manual upload mode**, if the PDB structure provided by the user does not contain any small molecule ligands, **DrugReAlign** will automatically search for small molecule ligands from proteins with similar sequences using RCSB PDB. These ligands will be docked with the user's uploaded PDB structure.

After docking, the interaction information from the docked complex will be used to generate a prompt template, which will then be utilized to interact with large language models (LLMs) to provide insights or predictions.

This process ensures that even if the original structure lacks ligands, **DrugReAlign** will attempt to provide a complete interaction analysis by identifying relevant small molecule ligands.

## Demonstration Video

For a detailed walkthrough, please refer to the demonstration video:
[![DrugReAlign-Usage Example]](DrugReAlign-Usage_Example.mp4)

# Experimental Data and Interpretation

## Download

Experimental data is available for download from the provided link. Navigate to the [Experimental Data](https://github.com/kkkayle/DrugReAlign/tree/master/Experimental) directory.

## Data Structure and Interpretation

The experimental data is organized as follows:

```
📂 Experimental data
  ┣ 📂 LLMs_Answers (Subject experimental data in the paper)
  ┣ 📂 Docking_results (Molecular docking conducted in the main experiment and the spatial information removal experiment)
  ┣ 📂 Table1_DL_result
  ┣ 📂 Ablation (Results from LLMs with spatial information removed and predictions from traditional deep learning models)
    ┣ 📂 newbing
    ┣ 📂 gpt4
    ┣ 📂 gpt3
    ┣ 📂 medllama3
    ┣ 📂 DL_Answers
      ┣ 📂 TransformerCPI2.0 (Model's prediction results)
      ┣ 📂 Drugban (Model's prediction results)
      ┗ 📂 DL_docking_results (Docking results of the models mentioned above)
```

# Custom Data Input

DrugReAlign supports two modes for custom input: **manual_upload** and **sequence_search**.

### Configuration File (config.yaml)

To run the project with custom input data, create or modify a configuration file (`config.yaml`) with the following structure:

#### 1. Manual PDB Upload Mode

In this mode, users can manually provide a PDB file and optional summary information. Example:

```yaml
mode: manual_upload  # Options: "manual_upload", "sequence_search"

manual_upload:
  pdb_file_path: "./temp/1A5Y.pdb"  # Path to the manually uploaded PDB file
  use_summary: true  # Boolean value, whether to use summary information manually provided by the user
  summary_info:  # Summary information provided by the user, required if `use_summary` is true
    Title: "CRYSTAL STRUCTURE OF HUMAN NAD[P]H-QUINONE OXIDOREDUCTASE AT 1.7 A RESOLUTION"
    Classification: "OXIDOREDUCTASE"
    Organism(s): "Homo sapiens"
    Expression System: "Escherichia coli"
```

#### 2. Sequence Search Mode (RCSB PDB Search)

This mode allows users to input a protein sequence, and DrugReAlign will search the RCSB PDB for the most similar structure. Example:

```yaml
mode: sequence_search  # Options: "manual_upload", "sequence_search"

sequence_search:
  query_sequence: "MEEPQSDPSVEPPLSQETFSDLWKLLPEN"  # Query sequence for RCSB PDB search
  use_summary: false  # Boolean value, whether to use summary information manually provided by the user
  summary_info:  # Summary information provided by the user, required if `use_summary` is true
    Title: "Model Title Here"
    Classification: "Classification Here"
    Organism(s): "Organism Here"
    Expression System: "Expression System Here"
```

### Running the Project

Once the configuration file is ready:

1. Ensure that your input data is correctly referenced in the configuration file (`config.yaml`).
2. Run `DrugReAlign.py` to execute the analysis.
3. The results will be stored in the `result` folder, including any interaction details and docking outcomes.

### Additional Notes

- The `manual_upload` mode requires a valid PDB file path and optional summary metadata (title, classification, organism, etc.).
- The `sequence_search` mode accepts a protein sequence for searching similar structures in the RCSB PDB.
- The docking results will be provided in both `.pdb` and `.csv` formats, and ligand interaction data will be saved for visualization purposes.



### Multithreading Support

We have now implemented multithreading to speed up the processing of large datasets. This new feature enables the parallel execution of `DrugReAlign.py` and `DrugReAlign-Custom Data.py` for multiple PDB files or configuration files, respectively.

#### Key Functions:
1. **Parallel Processing for DrugReAlign:**
   - You can process multiple PDB entries listed in a CSV file in parallel using the `process_drugrealign_csv` function.
   - The number of threads can be configured using the `--threads` argument, with the default set to 4 threads.
   - The command looks like:
     ```bash
     python DrugReAlign.py --mode Normal --csv <path_to_csv> --threads <num_threads>
     ```

2. **Parallel Processing for DrugReAlign-Custom Data:**
   - For custom data processing, multiple configuration files can be handled concurrently by the `process_custom_data_folder` function.
   - Similar to PDB processing, you can configure the number of threads to use with the `--threads` argument.
   - The command looks like:
     ```bash
     python DrugReAlign.py --mode Custom --config_folder <path_to_config_folder> --threads <num_threads>
     ```

#### Example Usage:
- To process a CSV file of PDB entries using 12 threads:
  ```bash
  python DrugReAlign.py --mode Normal --csv ./batch_input/DrugReAlign/input.csv --threads 12
  ```

- To process a folder of custom configuration files using 8 threads:
  ```bash
  python DrugReAlign.py --mode Custom --config_folder ./batch_input/DrugReAlign-Custom Data --threads 8
  ```

By utilizing multithreading, the overall processing time can be significantly reduced, especially when working with large datasets.
