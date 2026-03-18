import os
from typing import Dict, Any
from mp_api.client import MPRester
from state import STATE

MP_API_KEY = os.getenv("MP_API_KEY")


def fetch_structure(material: str) -> Dict[str, Any]:
    with MPRester(MP_API_KEY) as mpr:
        docs = mpr.materials.summary.search(
            formula=material,
            fields=["material_id"]
        )

        if not docs:
            return {"ok": False, "error": "No material found"}

        mp_id = str(docs[0].material_id)
        structure = mpr.get_structure_by_material_id(mp_id)

    STATE["structure"] = structure
    STATE["material_id"] = mp_id

    return {
        "ok": True,
        "material_id": mp_id,
        "num_atoms": len(structure)
    }


def make_supercell(scaling: list[int]) -> Dict[str, Any]:
    structure = STATE.get("structure")

    if structure is None:
        return {"ok": False, "error": "No structure loaded"}

    structure = structure.copy()
    structure.make_supercell(scaling)

    STATE["structure"] = structure

    return {
        "ok": True,
        "num_atoms": len(structure)
    }


def save_poscar(filename: str = "POSCAR") -> Dict[str, Any]:
    structure = STATE.get("structure")

    if structure is None:
        return {"ok": False, "error": "No structure loaded"}

    structure.to(filename=filename, fmt="poscar")
    return {"ok": True, "file": filename}


def save_cif(filename: str = "structure.cif") -> Dict[str, Any]:
    structure = STATE.get("structure")

    if structure is None:
        return {"ok": False, "error": "No structure loaded"}

    structure.to(filename=filename, fmt="cif")
    return {"ok": True, "file": filename}


def describe_structure() -> Dict[str, Any]:
    structure = STATE.get("structure")

    if structure is None:
        return {"ok": False, "error": "No structure loaded"}

    return {
        "ok": True,
        "formula": structure.composition.formula,
        "num_atoms": len(structure)
    }


TOOLS = {
    "fetch_structure": fetch_structure,
    "make_supercell": make_supercell,
    "save_poscar": save_poscar,
    "save_cif": save_cif,
    "describe_structure": describe_structure,
}