import os, dspy
from dotenv import load_dotenv

load_dotenv()
open_ai_key = os.getenv("open_ai_key")            # .env: open_ai_key=sk-...

lm = dspy.LM("openai/gpt-4o-mini", api_key=open_ai_key)
dspy.configure(lm=lm)                             # one configure is enough

# ---- Signatures ----
class MoleculeSignature(dspy.Signature):
    """Extract molecule names from a text passage."""
    text = dspy.InputField(desc="Text containing molecule names")
    molecule_names = dspy.OutputField(
        type=str, desc="Text containing molecule names",
        format=list                    # DSPy parses into a list
    )

class SmilesSignature(dspy.Signature):
    """Return SMILES for the given molecule name."""
    molecule_name = dspy.InputField(desc="Name of the molecule")
    smiles = dspy.OutputField(desc="SMILES string")

class SmilesCompareSignature(dspy.Signature):
    """Check if two SMILES strings are identical."""
    smiles1 = dspy.InputField()
    smiles2 = dspy.InputField()
    is_equal = dspy.OutputField(format=bool, desc="True/False")

# ---- Predictors ----
molecule_module       = dspy.Predict(MoleculeSignature)
smiles_module         = dspy.Predict(SmilesSignature)
smiles_compare_module = dspy.Predict(SmilesCompareSignature)

# ---- Demo ----
text_input = "Aspirin and ibuprofen are common painkillers."
mols = molecule_module(text=text_input).molecule_names
s1   = smiles_module(molecule_name=mols[0]).smiles
s2   = smiles_module(molecule_name=mols[1]).smiles
equal = smiles_compare_module(smiles1=s1, smiles2=s2).is_equal
print(mols, equal)
