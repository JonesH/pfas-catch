"""Main file rendering the APIs"""
import sys
from pathlib import Path
from fastapi import FastAPI,Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
# from src.audio_utils import text_to_speech
from src.utils import get_filename, get_molecules, get_smiles
from src.utils import (
    get_best_adsorber_for_pfas,
    get_best_adsorber_pfas_table,
    get_filename,
    get_molecules,
    get_smiles,
)

app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def get_pfas_match_root():
    """Base API for PFAS to Adsorber match"""
    return {"PFAS": "DETA-adsorber"}


@app.post("/smiles")
async def get_smiles_from_text(text: str):
    """Get the SMILES representation from the given text description of the molecule"""
    molecule_names = get_molecules(text)
    return [get_smiles(molecule_name) for molecule_name in molecule_names]


@app.post("/render2d")
async def get_2d_render_from_smiles(smiles: str) -> FileResponse:
    smiles = smiles.strip().strip('"')  # Remove whitespace and quotes
    filename_base = get_filename(smiles)
    if filename_base is None:
        raise ValueError(f"Could not generate filename from smiles: {smiles}")

    filename = filename_base + ".jpg"
    file_path = Path("images") / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Image file not found at {file_path}")

    return FileResponse(file_path, media_type="image/jpg")


@app.post("/render3d")
async def get_3d_render_from_smiles(smiles: str) -> FileResponse:
    smiles = smiles.strip().strip('"')  # Remove whitespace and quotes
    filename_base = get_filename(smiles)
    if filename_base is None:
        raise ValueError(f"Could not generate filename from smiles: {smiles}")

    filename = filename_base + "_gaff.mol2"
    file_path = Path("images") / filename
    if not file_path.exists():
        raise FileNotFoundError(f"3D file not found at {file_path}")

    return FileResponse(file_path)


# @app.post("/text2imagefiles")
# async def get_images_from_text(text: str):
#
# #     """Returns a list of image files from the text description of the molecule"""
#     molecule_names = get_molecules(text)
#     return molecule_names
#     images = []
#     mol2_files = []
#     images_adsorbers = []
#     mol2_files_adsorbers = []
#     pfas_table_dict = {}
#     # for molecule_name in molecule_names:
#         # smiles = get_smiles(molecule_name)
#         # filename = get_filename(smiles) + ".jpg"
#         # file_path = Path("images") / filename
#         # images.append(FileResponse(file_path, media_type="image/jpg"))
# #
#         # mol2_filename = get_filename(smiles) + "_gaff.mol2"
#         # mol2_file_path = Path("images") / mol2_filename
#         # mol2_files.append(FileResponse(mol2_file_path, media_type="text/mol2"))
#         # if "per-fluoro" in molecule_name:
#             # if the molecule is a PFAS, get the best adsorber for it
#             # adsorber = get_best_adsorber_for_pfas(molecule_name)
# #             if not adsorber:
# #                 continue
# #             adsorber_filename = f"{adsorber}.jpg"
# #             adsorber_file_path = Path("images") / adsorber_filename
# #             images_adsorbers.append(
# #                 FileResponse(adsorber_file_path, media_type="image/jpg")
# #             )
# #
# #             adsorber_mol2_filename = f"{adsorber}_gaff.mol2"
# #             adsorber_mol2_file_path = Path("images") / adsorber_mol2_filename
# #             mol2_files_adsorbers.append(
# #                 FileResponse(adsorber_mol2_file_path, media_type="text/mol2")
# #             )
# #             # Fetch the binding table for the PFAS
# #             pfas_table_dict = get_best_adsorber_pfas_table(molecule_name)
# #
# #     # output_text = f"Generated images for: {', '.join(molecule_names)}"
# #     # _ = await text_to_speech(output_text)
# #     return {
# #         "images_2d": images,
# #         "images_3d": mol2_files,
# #         "images_adsorbers": images_adsorbers,
# #         "mol2_files_adsorbers": mol2_files_adsorbers,
# #         "pfas_table": pfas_table_dict
# #     }
@app.post("/text2imagefiles")
async def get_images_from_text(text: str):
    """Returns a list of image files from the text description of the molecule"""
    molecule_names = get_molecules(text)
    images = []
    mol2_files = []
    images_adsorbers = []
    mol2_files_adsorbers = []
    pfas_table_dict = {}
    for molecule_name in molecule_names:
        smiles = get_smiles(molecule_name)
        filename = get_filename(smiles) + ".jpg"
        file_path = Path("images") / filename
        images.append(FileResponse(file_path, media_type="image/jpg"))

        mol2_filename = get_filename(smiles) + "_gaff.mol2"
        mol2_file_path = Path("images") / mol2_filename
        mol2_files.append(FileResponse(mol2_file_path, media_type="text/mol2"))
        if "per-fluoro" in molecule_name:
            # if the molecule is a PFAS
            # Fetch the binding table for the PFAS
            pfas_table_dict = get_best_adsorber_pfas_table(molecule_name)
            adsorber_name = pfas_table_dict[0]['DETA_variant']

    # output_text = f"Generated images for: {', '.join(molecule_names)}"
    # _ = await text_to_speech(output_text)
    return {
        "best_adsorber": adsorber_name,
        "pfas_table": pfas_table_dict
    }

if __name__ == "__main__":
    # T=get_images_from_text("PFBA")
    # print(T)
    import uvicorn
    uvicorn.run(app, host="127.0.3.1", port=8003)