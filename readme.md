# DrugReAlign
<p align="center">
  <img src="https://github.com/kkkayle/DrugReAlign/blob/master/DrugReAlign.png" width="400">
</p>



This guide outlines the process for utilizing your own data in drug repositioning projects. Follow the steps below to set up your environment and run analyses with custom datasets.

## System Requirements

Before you begin, ensure your system meets the following requirements:
- **Python Version:** 3.7.16
- **Required Libraries:**
  - numpy==1.21.5
  - pandas==1.3.5
  - plip==2.3.0
  - beautifulsoup4==4.9.3
  - requests==2.31.0
  - openai==1.12.0

## Setup Instructions

1. Ensure that the required libraries are installed in your Python environment.
2. Download the necessary PDB (Protein Data Bank) file, ensuring it includes a sample small molecule ligand binding, and the corresponding FASTA file.
3. Locate and modify the relevant file paths in the `DrugReAlign.ipynb` file according to your dataset.
4. Execute the notebook to run the analysis.
5. Results will be saved in the `./answer/` directory for further review.

# Experimental Data and Interpretation

## Download

Experimental data is available for download from the provided link. Navigate to the [Experimental Data](https://github.com/kkkayle/DrugReAlign/tree/master/Experimental%20data) directory.

## Data Structure and Interpretation

The experimental data is organized as follows:
```
📂 Experimental data
  ┣ 📂 LLMs_Answers (Subject experimental data in the paper)
  ┣ 📂 Docking_results (Molecular docking conducted in the main experiment and the spatial information removal experiment)
  ┣ 📂 Ablation (Results from LLMs with spatial information removed and predictions from traditional deep learning models)
    ┣ 📂 newbing
    ┣ 📂 gpt4
    ┣ 📂 gpt3
    ┣ 📂 DL_Answers
      ┣ 📂 TransformerCPI2.0 (Model's prediction results)
      ┣ 📂 Drugban (Model's prediction results)
      ┗ 📂 DL_docking_results (Docking results of the models mentioned above)
```
