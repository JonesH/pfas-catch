"""Constants for the repository"""

from enum import Enum
from pydantic import BaseModel


class Molecule(BaseModel):
    name: str
    smiles: str
    image: str
    iupac_name: str | None = None


pfba_molecule = Molecule(
    name="per-fluoro butanoic acid",
    smiles="O=C(O)C(F)(F)C(F)(F)C(F)(F)F",
    image="PFBA",
)
pfbs_molecule = Molecule(
    name="per-fluoro butane sulfonic acid",
    smiles="O=S(C(F)(F)C(F)(F)C(F)(F)C(F)(F)F)(O)=O",
    image="PFBS",
)
pfoa_molecule = Molecule(
    name="per-fluoro octanoic acid",
    smiles="O=C(O)C(F)(F)C(F)(F)C(C(F)(F)C(F)(F)C(C(F)(F)F)(F)F)(F)F",
    image="PFOA",
)
pfos_molecule = Molecule(
    name="per-fluoro octane sulfonic acid",
    smiles="O=S(C(F)(F)C(F)(F)C(F)(F)C(C(F)(F)C(F)(F)C(F)(F)C(F)(F)F)(F)F)(O)=O",
    image="PFOS",
)

adsorber_benzene = Molecule(
    name="ADSORBER Benzene",
    smiles="CC[N+](CC)(C)CC[N+](CC1CCCCC1)(C)CC[N+](CC)(C)CC",
    image="ADSORBER_benzene",
    iupac_name="N1-(cyclohexylmethyl)-N1-(2-(diethyl(methyl)ammonio)ethyl)-N2,N2-diethyl-N1,N2-dimethylethane-1,2-diaminium",
)

adsorber_cyclohexane = Molecule(
    name="ADSORBER Cyclohexane",
    smiles="CC[N+](CC)(C)CC[N+](CC1=CC=CC=C1)(C)CC[N+](CC)(C)CC",
    image="ADSORBER_cyclohexane",
    iupac_name="N1-benzyl-N1-(2-(diethyl(methyl)ammonio)ethyl)-N2,N2-diethyl-N1,N2-dimethylethane-1,2-diaminium",
)

adsorber_imidazole = Molecule(
    name="ADSORBER Imidazole",
    smiles="CC[N+](CC)(C)CC[N+](CC1=NC=CN1)(C)CC[N+](CC)(C)CC",
    image="ADSORBER_imidazole",
    iupac_name="N1-((1H-imidazol-2-yl)methyl)-N1-(2-(diethyl(methyl)ammonio)ethyl)-N2,N2-diethyl-N1,N2-dimethylethane-1,2-diaminium",
)

adsorber_nitrobenzene = Molecule(
    name="ADSORBER Nitrobenzene",
    smiles="CC[N+](CC)(C)CC[N+](CC1=CC=C([N+]([O-])=O)C=C1)(C)CC[N+](CC)(C)CC",
    image="ADSORBER_nitrobenzene",
    iupac_name="N1-(2-(diethyl(methyl)ammonio)ethyl)-N2,N2-diethyl-N1,N2-dimethyl-N1-(4-nitrobenzyl)ethane-1,2-diaminium",
)

adsorber_phenol = Molecule(
    name="ADSORBER Phenol",
    smiles="CC[N+](CC)(C)CC[N+](CC1=CC=C(O)C=C1)(C)CC[N+](CC)(C)CC",
    image="ADSORBER_phenol",
    iupac_name="N1-(2-(diethyl(methyl)ammonio)ethyl)-N2,N2-diethyl-N1-(4-hydroxybenzyl)-N1,N2-dimethylethane-1,2-diaminium",
)

adsorber_hexane = Molecule(
    name="ADSORBER Hexane",
    smiles="CC[N+](CC)(C)CC[N+](CCCCCCC)(C)CC[N+](CC)(C)CC",
    image="ADSORBER_hexane",
    iupac_name="N1-(2-(diethyl(methyl)ammonio)ethyl)-N2,N2-diethyl-N1-heptyl-N1,N2-dimethylethane-1,2-diaminium",
)

adsorber_isopentane = Molecule(
    name="ADSORBER Isopentane",
    smiles="CC[N+](CC)(C)CC[N+](CCC(C)CC(C)(C)C)(C)CC[N+](CC)(C)CC",
    image="ADSORBER_isopentane",
    iupac_name="N1-(2-(diethyl(methyl)ammonio)ethyl)-N2,N2-diethyl-N1,N2-dimethyl-N1-(3,5,5-trimethylhexyl)ethane-1,2-diaminium",
)


class MoleculeConstants(Enum):
    pfoa: Molecule = pfoa_molecule
    pfba: Molecule = pfba_molecule
    pfbs: Molecule = pfbs_molecule
    pfos: Molecule = pfos_molecule
    adsorber_benzene: Molecule = adsorber_benzene
    adsorber_cyclohexane: Molecule = adsorber_cyclohexane
    adsorber_imidazole: Molecule = adsorber_imidazole
    adsorber_nitrobenzene: Molecule = adsorber_nitrobenzene
    adsorber_phenol: Molecule = adsorber_phenol
    adsorber_hexane: Molecule = adsorber_hexane
    adsorber_isopentane: Molecule = adsorber_isopentane


best_adsorbers = {
    "per-fluoro butanoic acid": "ADSORBER_cyclohexane",
    "per-fluoro butane sulfonic acid": "ADSORBER_phenol",
    "per-fluoro octanoic acid": "ADSORBER_hexane",
    "per-fluoro octane sulfonic acid": "ADSORBER_hexane",
}
