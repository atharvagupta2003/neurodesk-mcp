"""
Neuroimaging MCP Server

A FastMCP server that provides neuroimaging analysis tools through the Model Context Protocol.
Integrates with NiWrap for containerized neuroimaging tool execution.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

from fastmcp import FastMCP, Context
import niwrap

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Neuroimaging MCP Server")

# Configure NiWrap for containerized execution
try:
    niwrap.use_docker()
    logger.info("Docker configured for NiWrap execution")
except Exception as e:
    logger.warning(f"Docker configuration failed: {e}")

@mcp.tool
async def fsl_bet_brain_extraction(
    input_file: str,
    ctx: Context,
    output_prefix: str = "brain_extracted",
    fractional_intensity: float = 0.5,
    generate_binary_mask: bool = True
) -> Dict[str, Any]:
    """Extract brain from skull using FSL BET

    Performs automated brain extraction from T1-weighted MRI images using
    FSL's Brain Extraction Tool (BET). Removes skull and non-brain tissue
    while preserving brain structure.

    Args:
        input_file: Path to input T1-weighted MRI image (NIfTI format)
        output_prefix: Prefix for output files (default: "brain_extracted")
        fractional_intensity: Brain/non-brain threshold (0-1, default: 0.5)
        generate_binary_mask: Generate binary brain mask (default: True)

    Returns:
        Dict containing paths to extracted brain image and mask
    """

    await ctx.info(f"Starting brain extraction with BET on {input_file}")

    # Validate inputs
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    try:
        # Prepare output paths
        output_dir = Path("/Users/hp/Desktop/neurodesk/data/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        brain_image = str(output_dir / f"{output_prefix}.nii.gz")

        await ctx.info(f"Running FSL BET with fractional intensity: {fractional_intensity}")

        # Execute BET using NiWrap
        bet_params = {
            "infile": input_file,
            "maskfile": brain_image,
            "fractional_intensity": fractional_intensity
        }

        if generate_binary_mask:
            bet_params["binary_mask"] = True

        result = niwrap.fsl.bet(**bet_params)

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

        await ctx.info("Brain extraction completed successfully")
        return output_data

    except Exception as e:
        await ctx.error(f"BET processing failed: {str(e)}")
        raise RuntimeError(f"BET processing failed: {str(e)}")

@mcp.tool
async def fsl_fast_segmentation(
    input_file: str,
    ctx: Context,
    output_prefix: str = "segmented",
    tissue_classes: int = 3
) -> Dict[str, Any]:
    """Segment brain tissue into different classes using FSL FAST

    Performs automated segmentation of brain tissue into gray matter,
    white matter, and cerebrospinal fluid using FSL FAST.

    Args:
        input_file: Path to brain-extracted T1-weighted image
        output_prefix: Prefix for output files (default: "segmented")
        tissue_classes: Number of tissue classes (default: 3)

    Returns:
        Dict containing paths to tissue segmentation maps
    """

    await ctx.info(f"Starting tissue segmentation with FAST on {input_file}")

    # Validate inputs
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    try:
        # Prepare output path
        output_dir = Path("/Users/hp/Desktop/neurodesk/data/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)

        await ctx.info(f"Running FSL FAST with {tissue_classes} tissue classes")

        # Execute FAST using NiWrap
        fast_params = {
            "infile": input_file,
            "basename": str(output_dir / output_prefix),
            "classes": tissue_classes,
            "bias_field": True,
            "probability_maps": True
        }

        result = niwrap.fsl.fast(**fast_params)

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

        await ctx.info("Tissue segmentation completed successfully")
        return output_data

    except Exception as e:
        await ctx.error(f"FAST processing failed: {str(e)}")
        raise RuntimeError(f"FAST processing failed: {str(e)}")

@mcp.tool
async def fsl_flirt_registration(
    input_file: str,
    reference_file: str,
    ctx: Context,
    output_file: str = "registered.nii.gz",
    dof: int = 12
) -> Dict[str, Any]:
    """Register image to reference space using FSL FLIRT

    Performs linear registration of an input image to a reference image
    using FSL FLIRT (FMRIB's Linear Image Registration Tool).

    Args:
        input_file: Path to input image to be registered
        reference_file: Path to reference image
        output_file: Path for output registered image
        dof: Degrees of freedom for registration (6, 7, 9, or 12)

    Returns:
        Dict containing path to registered image and transformation matrix
    """

    await ctx.info(f"Starting registration with FLIRT: {input_file} -> {reference_file}")

    # Validate inputs
    input_path = Path(input_file)
    ref_path = Path(reference_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    if not ref_path.exists():
        raise FileNotFoundError(f"Reference file not found: {reference_file}")

    try:
        await ctx.info(f"Running FSL FLIRT with {dof} degrees of freedom")

        # Execute FLIRT using NiWrap
        flirt_params = {
            "infile": input_file,
            "reference": reference_file,
            "outfile": output_file,
            "dof": dof,
            "cost": "corratio"
        }

        result = niwrap.fsl.flirt(**flirt_params)

        output_data = {
            "registered_image": result.outfile,
            "transformation_matrix": getattr(result, 'omat', None),
            "metadata": {
                "tool": "FSL FLIRT",
                "parameters": flirt_params,
                "dof": dof
            }
        }

        await ctx.info("Registration completed successfully")
        return output_data

    except Exception as e:
        await ctx.error(f"FLIRT processing failed: {str(e)}")
        raise RuntimeError(f"FLIRT processing failed: {str(e)}")

@mcp.tool
async def mrtrix_dwi2fod(
    dwi_file: str,
    response_file: str,
    ctx: Context,
    output_fod: str = "wmfod.mif",
    algorithm: str = "csd"
) -> Dict[str, Any]:
    """Estimate fiber orientation distributions using MRTrix3

    Computes fiber orientation distributions (FODs) from diffusion-weighted
    imaging data using constrained spherical deconvolution.

    Args:
        dwi_file: Path to diffusion-weighted image
        response_file: Path to response function file
        output_fod: Path for output FOD image
        algorithm: Algorithm to use (csd, msmt_csd)

    Returns:
        Dict containing path to FOD image and metadata
    """

    await ctx.info(f"Starting FOD estimation with dwi2fod on {dwi_file}")

    # Validate inputs
    dwi_path = Path(dwi_file)
    response_path = Path(response_file)

    if not dwi_path.exists():
        raise FileNotFoundError(f"DWI file not found: {dwi_file}")
    if not response_path.exists():
        raise FileNotFoundError(f"Response file not found: {response_file}")

    try:
        await ctx.info(f"Running MRTrix3 dwi2fod with {algorithm} algorithm")

        # Execute dwi2fod using NiWrap
        dwi2fod_params = {
            "algorithm": algorithm,
            "dwi": dwi_file,
            "response": response_file,
            "fod": output_fod
        }

        result = niwrap.mrtrix3.dwi2fod(**dwi2fod_params)

        output_data = {
            "fod_image": result.fod,
            "metadata": {
                "tool": "MRTrix3 dwi2fod",
                "parameters": dwi2fod_params,
                "algorithm": algorithm
            }
        }

        await ctx.info("FOD estimation completed successfully")
        return output_data

    except Exception as e:
        await ctx.error(f"dwi2fod processing failed: {str(e)}")
        raise RuntimeError(f"dwi2fod processing failed: {str(e)}")

@mcp.tool
async def freesurfer_recon_all(
    input_file: str,
    subject_id: str,
    ctx: Context,
    subjects_dir: str = "/Users/hp/Desktop/neurodesk/data/freesurfer_subjects"
) -> Dict[str, Any]:
    """Run FreeSurfer cortical reconstruction pipeline

    Performs complete cortical surface reconstruction and analysis
    using FreeSurfer's recon-all pipeline.

    Args:
        input_file: Path to T1-weighted MRI image
        subject_id: Subject identifier for FreeSurfer
        subjects_dir: FreeSurfer subjects directory

    Returns:
        Dict containing paths to FreeSurfer outputs and metadata
    """

    await ctx.info(f"Starting FreeSurfer recon-all for subject {subject_id}")

    # Validate inputs
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Create subjects directory
    subjects_path = Path(subjects_dir)
    subjects_path.mkdir(parents=True, exist_ok=True)

    try:
        await ctx.info("Running FreeSurfer recon-all (this may take several hours)")

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

        await ctx.info("FreeSurfer recon-all completed successfully")
        return output_data

    except Exception as e:
        await ctx.error(f"FreeSurfer recon-all failed: {str(e)}")
        raise RuntimeError(f"FreeSurfer recon-all failed: {str(e)}")

@mcp.resource("neuroimaging://workspace/{session_id}")
async def get_workspace_info(session_id: str) -> str:
    """Get information about a neuroimaging workspace session"""
    workspace_path = Path(f"/tmp/neuroimaging_workspace/{session_id}")

    if not workspace_path.exists():
        return f"Workspace {session_id} not found"

    files = list(workspace_path.glob("*"))
    file_list = "\n".join([f"- {f.name}" for f in files])

    return f"Workspace {session_id}:\nFiles:\n{file_list}"

@mcp.prompt
def neuroimaging_analysis_guide(analysis_type: str) -> str:
    """Generate a prompt for neuroimaging analysis guidance"""

    guides = {
        "brain_extraction": """
        Brain extraction is the first step in most neuroimaging analyses. Here's a typical workflow:

        1. Start with a T1-weighted anatomical image
        2. Use FSL BET with appropriate fractional intensity (0.3-0.7)
        3. Visual quality control of extraction results
        4. Proceed with further analysis on brain-extracted image

        Parameters to consider:
        - Lower fractional intensity (0.3) for more conservative extraction
        - Higher fractional intensity (0.7) for more aggressive extraction
        - Default (0.5) works well for most cases
        """,

        "preprocessing": """
        Standard T1 preprocessing pipeline:

        1. Brain extraction (BET)
        2. Tissue segmentation (FAST)
        3. Spatial normalization (FLIRT to MNI space)
        4. Quality control at each step

        This pipeline prepares data for group-level statistical analysis.
        """,

        "diffusion": """
        Diffusion MRI analysis workflow:

        1. Preprocessing: denoising, motion correction, eddy current correction
        2. Response function estimation
        3. Fiber orientation distribution estimation (dwi2fod)
        4. Tractography generation
        5. Connectome construction

        Requires DWI data with b-values and gradient directions.
        """
    }

    return guides.get(analysis_type, "Unknown analysis type. Available types: brain_extraction, preprocessing, diffusion")

def main():
    """Main entry point for the MCP server"""
    logger.info("Starting Neuroimaging MCP Server...")
    mcp.run()

if __name__ == "__main__":
    main()