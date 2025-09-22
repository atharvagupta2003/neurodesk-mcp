#!/usr/bin/env python3
"""
Create synthetic test data for neuroimaging MCP server testing
"""

import numpy as np
import nibabel as nib
from pathlib import Path

def create_synthetic_t1():
    """Create synthetic T1-weighted image"""
    print("Creating synthetic T1-weighted image...")

    shape = (182, 218, 182)  # Standard MNI dimensions
    data = np.random.random(shape) * 1000

    # Create brain-like structure
    center = np.array(shape) // 2
    xx, yy, zz = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]), np.arange(shape[2]), indexing='ij')
    distance = np.sqrt((xx - center[0])**2 + (yy - center[1])**2 + (zz - center[2])**2)
    brain_mask = distance < 60
    data[~brain_mask] *= 0.1  # Reduce signal outside "brain"

    # Add some tissue contrast
    # White matter (higher intensity)
    wm_mask = (distance < 45) & (distance > 25)
    data[wm_mask] *= 1.2

    # Gray matter (medium intensity)
    gm_mask = (distance < 55) & (distance > 45)
    data[gm_mask] *= 0.8

    # Save as NIfTI
    img = nib.Nifti1Image(data.astype(np.float32), np.eye(4))
    output_path = Path('/Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(img, output_path)
    print(f"✓ Created synthetic T1 image: {output_path}")
    return output_path

def create_mni_template():
    """Create simple MNI-like template"""
    print("Creating synthetic MNI template...")

    shape = (182, 218, 182)
    data = np.random.random(shape) * 800 + 200  # Different intensity distribution

    # Create a slightly different brain shape for registration target
    center = np.array(shape) // 2
    xx, yy, zz = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]), np.arange(shape[2]), indexing='ij')
    distance = np.sqrt((xx - center[0])**2 + (yy - center[1])**2 + (zz - center[2])**2)
    brain_mask = distance < 65  # Slightly larger
    data[~brain_mask] *= 0.05

    img = nib.Nifti1Image(data.astype(np.float32), np.eye(4))
    output_path = Path('/Users/hp/Desktop/neurodesk/data/templates/synthetic_mni.nii.gz')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(img, output_path)
    print(f"✓ Created synthetic MNI template: {output_path}")
    return output_path

def create_diffusion_data():
    """Create minimal diffusion data for testing"""
    print("Creating synthetic diffusion data...")

    # Create DWI data (simplified)
    shape = (96, 96, 60, 33)  # x, y, z, directions (32 + 1 b0)
    data = np.random.random(shape) * 1000

    # Create brain mask for DWI
    center = np.array(shape[:3]) // 2
    xx, yy, zz = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]), np.arange(shape[2]), indexing='ij')
    distance = np.sqrt((xx - center[0])**2 + (yy - center[1])**2 + (zz - center[2])**2)
    brain_mask = distance < 30

    # Apply brain mask to all volumes
    for vol in range(shape[3]):
        data[:, :, :, vol][~brain_mask] *= 0.1

    # Save DWI data
    img = nib.Nifti1Image(data.astype(np.float32), np.eye(4))
    output_path = Path('/Users/hp/Desktop/neurodesk/data/diffusion/synthetic_dwi.nii.gz')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(img, output_path)

    # Create b-values file (1 b0 + 32 directions at b=1000)
    bvals = [0] + [1000] * 32
    bval_path = output_path.with_suffix('.bval')
    with open(bval_path, 'w') as f:
        f.write(' '.join(map(str, bvals)) + '\n')

    # Create b-vectors file (simplified gradient directions)
    bvecs = []
    bvecs.append([0, 0, 0])  # b0 direction

    # Generate 32 random unit vectors
    for i in range(32):
        vec = np.random.randn(3)
        vec = vec / np.linalg.norm(vec)
        bvecs.append(vec)

    bvec_path = output_path.with_suffix('.bvec')
    with open(bvec_path, 'w') as f:
        for dim in range(3):
            line = ' '.join([f"{bvec[dim]:.6f}" for bvec in bvecs])
            f.write(line + '\n')

    print(f"✓ Created synthetic DWI data: {output_path}")
    print(f"✓ Created b-values file: {bval_path}")
    print(f"✓ Created b-vectors file: {bvec_path}")

    return output_path, bval_path, bvec_path

def create_response_function():
    """Create a simple response function file for MRTrix3"""
    print("Creating synthetic response function...")

    # Simple response function (single shell, single tissue)
    # Format: l values followed by response amplitudes
    response_data = [
        "# Response function for single shell, single tissue",
        "# Generated synthetically for testing",
        "0 1.0",
        "2 0.3",
        "4 0.1",
        "6 0.05",
        "8 0.02"
    ]

    response_path = Path('/Users/hp/Desktop/neurodesk/data/diffusion/synthetic_response.txt')
    response_path.parent.mkdir(parents=True, exist_ok=True)

    with open(response_path, 'w') as f:
        f.write('\n'.join(response_data) + '\n')

    print(f"✓ Created synthetic response function: {response_path}")
    return response_path

def create_directory_structure():
    """Create all necessary directories"""
    directories = [
        '/Users/hp/Desktop/neurodesk/data/t1_structural',
        '/Users/hp/Desktop/neurodesk/data/diffusion',
        '/Users/hp/Desktop/neurodesk/data/templates',
        '/Users/hp/Desktop/neurodesk/data/freesurfer_subjects',
        '/Users/hp/Desktop/neurodesk/data/outputs'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def main():
    """Create all test data"""
    print("🧠 Creating test data for Neuroimaging MCP Server\n")

    # Create directory structure
    create_directory_structure()
    print()

    # Create synthetic data
    t1_path = create_synthetic_t1()
    mni_path = create_mni_template()
    dwi_path, bval_path, bvec_path = create_diffusion_data()
    response_path = create_response_function()

    print("\n✅ All test data created successfully!")
    print("\n📁 Test data locations:")
    print(f"   T1 structural: {t1_path}")
    print(f"   MNI template:  {mni_path}")
    print(f"   DWI data:      {dwi_path}")
    print(f"   Response func: {response_path}")

    print("\n🚀 You can now test the MCP server with:")
    print("   cd /Users/hp/Desktop/neurodesk/mcp")
    print("   python src/server.py")

    print("\n📖 See TEST_DATA_GUIDE.md for detailed usage instructions")

if __name__ == "__main__":
    main()