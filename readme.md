# DrugReAlign
<p align="center">
  <img src="https://github.com/kkkayle/DrugReAlign/blob/master/DrugReAlign.png" width="400">
</p>



This guide outlines the process for utilizing your own data in drug repositioning projects. Follow the steps below to set up your environment and run analyses with custom datasets.

## System Requirements
Note:If you need to automate molecular docking, you need to use a Linux system (or manually configure the Vina path on other systems)

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
  - vina==1.2.5(Linux)
  - biopython==1.83
  - rich==13.7.1
  - openbabel==3.1.1
  - pymol-open-source==3.0.0

- **MGLTOOLS:** no specific version requirements.
## Setup Instructions

1. Ensure that the required libraries are installed in your Python environment.
2. Please fill in the api_key and change the model (if necessary) in DrugReAlign.py.
3. Please fill in the MGLTOOLS path in config/PDBConverter.py.
4. Run DrugReAlign.py to perform the analysis.
5. The results will be saved in the result directory for further review.

## Demonstration Video

For a detailed walkthrough, please refer to the demonstration video:
[![DrugReAlign-Usage Example]](DrugReAlign-Usage_Example.mp4)

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
