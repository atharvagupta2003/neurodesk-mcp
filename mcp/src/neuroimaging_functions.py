"""
Raw neuroimaging functions for testing without MCP decorators
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

import niwrap

logger = logging.getLogger(__name__)

# Configure NiWrap for containerized execution
try:
    niwrap.use_docker()
    logger.info("Docker configured for NiWrap execution")
except Exception as e:
    logger.warning(f"Docker configuration failed: {e}")

async def fsl_bet_brain_extraction_raw(
    input_file: str,
    output_prefix: str = "brain_extracted",
    fractional_intensity: float = 0.5,
    generate_binary_mask: bool = True
) -> Dict[str, Any]:
    """Extract brain from skull using FSL BET (raw function for testing)"""

    print(f"Starting brain extraction with BET on {input_file}")

    # Validate inputs
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    try:
        # Prepare output paths
        output_dir = Path("/Users/hp/Desktop/neurodesk/data/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        brain_image = str(output_dir / f"{output_prefix}.nii.gz")

        print(f"Running FSL BET with fractional intensity: {fractional_intensity}")

        # Execute BET using NiWrap
        result = niwrap.fsl.bet(
            infile=input_file,
            maskfile=brain_image,
            fractional_intensity=fractional_intensity,
            binary_mask=generate_binary_mask
        )

        output_data = {
            "brain_image": result.outfile,
            "metadata": {
                "tool": "FSL BET",
                "parameters": bet_params,
                "container": "FSL Docker container"
            }
        }

        if generate_binary_mask and hasattr(result, 'binary_mask'):
            output_data["brain_mask"] = result.binary_mask

        print("Brain extraction completed successfully")
        return output_data

    except Exception as e:
        print(f"BET processing failed: {str(e)}")
        raise RuntimeError(f"BET processing failed: {str(e)}")

async def fsl_fast_segmentation_raw(
    input_file: str,
    output_prefix: str = "segmented",
    tissue_classes: int = 3
) -> Dict[str, Any]:
    """Segment brain tissue into different classes using FSL FAST (raw function)"""

    print(f"Starting tissue segmentation with FAST on {input_file}")

    # Validate inputs
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    try:
        # Prepare output path
        output_dir = Path("/Users/hp/Desktop/neurodesk/data/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Running FSL FAST with {tissue_classes} tissue classes")

        # Execute FAST using NiWrap
        result = niwrap.fsl.fast(
            in_files=[input_file],
            number_classes=tissue_classes,
            out_basename=str(output_dir / output_prefix),
            output_biasfield=True,
            segments=True
        )

        output_data = {
            "segmented_image": result.outfile,
            "tissue_maps": getattr(result, 'tissue_maps', []),
            "bias_field": getattr(result, 'bias_field', None),
            "metadata": {
                "tool": "FSL FAST",
                "parameters": fast_params,
                "tissue_classes": tissue_classes
            }
        }

        print("Tissue segmentation completed successfully")
        return output_data

    except Exception as e:
        print(f"FAST processing failed: {str(e)}")
        raise RuntimeError(f"FAST processing failed: {str(e)}")

async def fsl_flirt_registration_raw(
    input_file: str,
    reference_file: str,
    output_file: str = "registered.nii.gz",
    dof: int = 12
) -> Dict[str, Any]:
    """Register image to reference space using FSL FLIRT (raw function)"""

    print(f"Starting registration with FLIRT: {input_file} -> {reference_file}")

    # Validate inputs
    input_path = Path(input_file)
    ref_path = Path(reference_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    if not ref_path.exists():
        raise FileNotFoundError(f"Reference file not found: {reference_file}")

    try:
        print(f"Running FSL FLIRT with {dof} degrees of freedom")

        # Execute FLIRT using NiWrap
        result = niwrap.fsl.flirt(
            in_file=input_file,
            reference=reference_file,
            out_file=output_file,
            out_matrix_file=output_file.replace('.nii.gz', '.mat'),
            dof=dof,
            cost="corratio"
        )

        output_data = {
            "registered_image": result.outfile,
            "transformation_matrix": getattr(result, 'omat', None),
            "metadata": {
                "tool": "FSL FLIRT",
                "parameters": flirt_params,
                "dof": dof
            }
        }

        print("Registration completed successfully")
        return output_data

    except Exception as e:
        print(f"FLIRT processing failed: {str(e)}")
        raise RuntimeError(f"FLIRT processing failed: {str(e)}")

async def mrtrix_dwi2fod_raw(
    dwi_file: str,
    response_file: str,
    output_fod: str = "wmfod.mif",
    algorithm: str = "csd"
) -> Dict[str, Any]:
    """Estimate fiber orientation distributions using MRTrix3 (raw function)"""

    print(f"Starting FOD estimation with dwi2fod on {dwi_file}")

    # Validate inputs
    dwi_path = Path(dwi_file)
    response_path = Path(response_file)

    if not dwi_path.exists():
        raise FileNotFoundError(f"DWI file not found: {dwi_file}")
    if not response_path.exists():
        raise FileNotFoundError(f"Response file not found: {response_file}")

    try:
        print(f"Running MRTrix3 dwi2fod with {algorithm} algorithm")

        # Execute dwi2fod using NiWrap
        dwi2fod_params = {
            "algorithm": algorithm,
            "dwi": dwi_file,
            "response": response_file,
            "fod": output_fod
        }

        result = niwrap.mrtrix.dwi2fod(**dwi2fod_params)

        output_data = {
            "fod_image": result.fod,
            "metadata": {
                "tool": "MRTrix3 dwi2fod",
                "parameters": dwi2fod_params,
                "algorithm": algorithm
            }
        }

        print("FOD estimation completed successfully")
        return output_data

    except Exception as e:
        print(f"dwi2fod processing failed: {str(e)}")
        raise RuntimeError(f"dwi2fod processing failed: {str(e)}")

async def freesurfer_recon_all_raw(
    input_file: str,
    subject_id: str,
    subjects_dir: str = "/Users/hp/Desktop/neurodesk/data/freesurfer_subjects"
) -> Dict[str, Any]:
    """Run FreeSurfer cortical reconstruction pipeline (raw function)"""

    print(f"Starting FreeSurfer recon-all for subject {subject_id}")

    # Validate inputs
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Create subjects directory
    subjects_path = Path(subjects_dir)
    subjects_path.mkdir(parents=True, exist_ok=True)

    try:
        print("Running FreeSurfer recon-all (this may take several hours)")

        # Execute recon-all using NiWrap
        recon_params = {
            "input_file": input_file,
            "subject_id": subject_id,
            "subjects_dir": subjects_dir,
            "all": True  # Run all processing stages
        }

        result = niwrap.freesurfer.recon_all(**recon_params)

        # FreeSurfer output structure
        subject_dir = subjects_path / subject_id

        output_data = {
            "subject_directory": str(subject_dir),
            "surfaces": {
                "left_pial": str(subject_dir / "surf" / "lh.pial"),
                "right_pial": str(subject_dir / "surf" / "rh.pial"),
                "left_white": str(subject_dir / "surf" / "lh.white"),
                "right_white": str(subject_dir / "surf" / "rh.white")
            },
            "volumes": {
                "brain": str(subject_dir / "mri" / "brain.mgz"),
                "aseg": str(subject_dir / "mri" / "aseg.mgz"),
                "aparc": str(subject_dir / "mri" / "aparc+aseg.mgz")
            },
            "metadata": {
                "tool": "FreeSurfer recon-all",
                "subject_id": subject_id,
                "subjects_dir": subjects_dir
            }
        }

        print("FreeSurfer recon-all completed successfully")
        return output_data

    except Exception as e:
        print(f"FreeSurfer recon-all failed: {str(e)}")
        raise RuntimeError(f"FreeSurfer recon-all failed: {str(e)}")