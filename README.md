# Description
This is an automated pipeline for docking of ligands to an arbitrary ADMET-related protein target. It uses the Application Programming Interface (API) of the TLDR platform (https://tldr.docking.org/) and UCSF DOCK 3.8 as the docking engine, both built by Irwin and Shoichet labs.

This pipeline works as follows: after a user provides SMILES of a ligand, the program generates its 3D conformational tree using the API of the TLDR platform. This process typically takes a few minutes, depending on the load of the infrastructure. Once the ligand file is prepared, the program conducts flexible docking to a binding site of interest and provides the result as a mol2 file, suitable for examination in most of the visualization software packages (UCSF Chimera, PyMOL, Avogadro, Jmol, etc.). Typically docking completes in under 5 seconds.

The structures of the proteins of interest may be obtained, among other sources, from the [Protein Data Bank](https://www.rcsb.org/), [AlphaFold predictions](https://github.com/choderalab/avoidome-analysis/tree/main/data/alphafold_downloads) and the [OpenADMET cofolding pipeline](https://github.com/OpenADMET/openadmet_toolkit/tree/main/openadmet_toolkit/structure). We have employed cytochrome P450 3A4 (PDB ID: 6MA71) as an example for the creation of the docking setup. 

# Installation
1. Apply for a license for UCSF DOCK 3.8 [here](https://dock.compbio.ucsf.edu/Online_Licensing/dock_license_application.html) and obtain the program. Note the path to `dock64` binary.
2. Create an account on https://tldr.docking.org and obtain your API key.
3. Download the files from this repository.

# Running
Prepare `config.yaml` file as follows and put it into the working directory.
```yaml
input_smi: "Fc1ccc(c(F)c1)C(O)(Cn2ncnc2)Cn3ncnc3"
API_TOKEN: "1aaaaaaaaaaaaaaa"
dock_executable: "/home/soft/dock38DOCK/ucsfdock/docking/DOCK/dock64"
dockfiles_dir: "/path/to/dockfiles_dir" # Update this path as needed
```
Run in the same directory `python automated_docking.py`

After completion of docking, see `output.mol2` in the working directory. Use `rec.pdb` from the `dockfiles` directory to visualize the docked pose.

If docking fails, check `dock/output/OUTDOCK` for the details.

# Funding
This work was supported by the Advanced Research Projects Agency for Health (ARPA-H) Award AY1AX000035.
