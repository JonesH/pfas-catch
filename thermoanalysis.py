"""Analyze the data from MD simulations and calculate binding free energy."""

from pathlib import Path
from analysis.thermodynamics import calculate_pmf_from_rdf

data_dir = Path("data/pfas_adsorber_combination")
pmf_data_dir = Path("data/pfas_adsorber_combination/pmf")
pmf_data_dir.mkdir(parents=True, exist_ok=True)

print("=== PMF Calculator from RDF ===")
print("Usage: python pmf_calculator.py")
print("Format: two columns (distance_nm, g_r)")

for fn in data_dir.glob("*.dat"):
    if "rdf" in fn.stem:
        rdf_file = fn
        file_path = data_dir / fn.name
        print(f"Processing RDF file: {file_path}")
        r, g_r, pmf, bind_dist, bind_energy = calculate_pmf_from_rdf(
            file_path, output_file=pmf_data_dir / f"{file_path.stem}_pmf.dat"
        )
