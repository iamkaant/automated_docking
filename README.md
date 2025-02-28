# Description
This is an automated pipeline for docking of ligands to cytochrome P450 3A4. It uses the Application Programming Interface (API) of the TLDR platform (https://tldr.docking.org/) and UCSF DOCK 3.8 as the docking engine, both built by Irwin and Shoichet labs.

This pipeline works as follows: after a user provides SMILES of a ligand, the program generates its 3D conformational tree using the API of the TLDR platform. This process typically takes a few minutes, depending on the load of the infrastructure. Once the ligand file is prepared, the program conducts flexible docking to the Cyp3A4 binding site and provides the result as a mol2 file, suitable for examination in most of the visualization software packages (UCSF Chimera, PyMOL, Avogadro, Jmol, etc.). Typically docking completes in under 5 seconds. 
We have used the structure with PDB ID: 6MA71 for the creation of the docking setup. 

# Installation
1. Apply for a license for UCSF DOCK 3.8 [here](https://dock.compbio.ucsf.edu/Online_Licensing/dock_license_application.html) and obtain the program. Note the path to `dock64` binary.
2. Create an account on https://tldr.docking.org and obtain your API key.
3. Download the files from this repository.

# Running
Prepare `config.yaml` file as follows and put it into the working directory.
```yaml
input_smi: "Fc1ccc(c(F)c1)C(O)(Cn2ncnc2)Cn3ncnc3"
working_dir: "/home/docking"
API_TOKEN: "1aaaaaaaaaaaaaaa"
dock_executable: "/home/soft/dock38DOCK/ucsfdock/docking/DOCK/dock64"
dockfiles_dir: "/path/to/dockfiles_dir" # Update this path as needed
```
Run in the same directory `python automated_docking.py`

After completion of docking, see `output.mol2` in the working directory. Use `rec.pdb` from the `dockfiles` directory to visualize the docked pose.

If docking fails, check `dock/output/OUTDOCK` for the details.
