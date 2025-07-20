"""Utilities for the PFAS catch/match application"""

from pathlib import Path

import pandas as pd
from src.constants import MoleculeConstants, best_adsorbers
from src.llm import molecule_module, smiles_module
# , geography_module)


def get_molecules(text: str) -> list:
    """Uses LLM to get the molecule name out of a given text description"""
    molecule_names_response = molecule_module(text=text)
    molecule_names = molecule_names_response.molecule_names
    if not molecule_names:
        return []
    return molecule_names


def get_smiles(molecule_name: str) -> str:
    """
    Uses LLM to match to the right SMILES representation of the molecule name
    """
    smiles_name_response = smiles_module(molecule_name=molecule_name)
    smiles_name = smiles_name_response.smiles
    # Compare smiles_name with existing ones
    smiles_name = smiles_name.strip()
    if not smiles_name:
        return ""
    return smiles_name


def get_filename(smiles: str):
    """Get the filename from a dictionary"""
    for mol in MoleculeConstants:
        if mol.value.smiles == smiles:
            return mol.value.image


def get_best_adsorber_for_pfas(pfas_name: str) -> str:
    """
    Get the best adsorber for a given PFAS name.
    """
    # Example implementation, replace with actual adsorber retrieval logic
    return best_adsorbers.get(pfas_name, None)


# def get_best_adsorber_pfas_table(pfas_name: str) -> dict:
#     """Get the sorted table of best adsorbers for a given PFAS"""
#     data_file = Path("data/best_pfas_deta_binding.csv")
#     df = pd.read_csv(data_file)
#     # Filter the DataFrame for the given PFAS name
#     filtered = df[df["PFAS"] == pfas_name]
#     # Sort the DataFrame by the "Binding Affinity" column
#     sorted_table = filtered.sort_values(
#         by="Binding_free_energy_kJ_mol", ascending=False
#     )
#     return sorted_table.to_dict(orient="records")

def get_best_adsorber_pfas_table(pfas_name: str) -> dict:
    """Get the sorted table of best adsorbers for a given PFAS"""
    data_file = Path("data/pfas_deta_binding.csv")
    df = pd.read_csv(data_file)
    # Filter the DataFrame for the given PFAS name
    for mol in MoleculeConstants:
        if mol.value.name == pfas_name:
            pfas_short_name = mol.name.upper()
            break
    filtered = df[df["PFAS"] == pfas_short_name]
    # Sort the DataFrame by the "Binding Affinity" column
    sorted_table = filtered.sort_values(by="Binding_free_energy_kJ_mol", ascending=True)
    return sorted_table.to_dict(orient="records")