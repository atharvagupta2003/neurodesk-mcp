# Test Data Guide for Neuroimaging MCP Server

This guide explains what test data to use for each MCP tool and where to obtain it.

## Directory Structure

```
/Users/hp/Desktop/neurodesk/data/
├── t1_structural/          # T1-weighted anatomical images
├── diffusion/             # Diffusion MRI data
├── templates/             # Reference templates (MNI, etc.)
├── freesurfer_subjects/   # FreeSurfer output directory
├── outputs/               # Tool outputs
└── TEST_DATA_GUIDE.md     # This file
```

## Test Data for Each Tool

### 1. FSL BET Brain Extraction

**Required Data:**
- T1-weighted anatomical MRI image in NIfTI format (.nii or .nii.gz)

**Test Data Sources:**
1. **OpenNeuro datasets** (recommended):
   ```bash
   # Download from OpenNeuro (example dataset)
   wget https://openneuro.org/crn/datasets/ds000001/snapshots/1.0.0/files/sub-01:anat:sub-01_T1w.nii.gz
   mv sub-01_T1w.nii.gz /Users/hp/Desktop/neurodesk/data/t1_structural/
   ```

2. **Create synthetic test data** (for quick testing):
   ```python
   import numpy as np
   import nibabel as nib

   # Create synthetic brain image
   shape = (182, 218, 182)  # Standard MNI dimensions
   data = np.random.random(shape) * 1000

   # Add brain-like structure
   center = np.array(shape) // 2
   xx, yy, zz = np.meshgrid(*[np.arange(s) for s in shape])
   distance = np.sqrt((xx - center[0])**2 + (yy - center[1])**2 + (zz - center[2])**2)
   brain_mask = distance < 60
   data[~brain_mask] *= 0.1

   # Save as NIfTI
   img = nib.Nifti1Image(data.astype(np.float32), np.eye(4))
   nib.save(img, '/Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz')
   ```

3. **Sample datasets**:
   - **OASIS-3**: https://www.oasis-brains.org/
   - **IXI Dataset**: https://brain-development.org/ixi-dataset/
   - **Human Connectome Project**: https://db.humanconnectome.org/

**Example Usage:**
```bash
# Test with synthetic data
python -c "
import asyncio
from fastmcp import Client

async def test():
    async with Client('src/server.py') as client:
        result = await client.call_tool('fsl_bet_brain_extraction', {
            'input_file': '/Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz',
            'fractional_intensity': 0.5
        })
        print(result)

asyncio.run(test())
"
```

### 2. FSL FAST Tissue Segmentation

**Required Data:**
- Brain-extracted T1-weighted image (output from BET)

**Test Data:**
- Use the output from FSL BET tool
- Or download pre-processed brain-extracted images

**Example Usage:**
```bash
# First run BET, then FAST
# Use the brain_extracted.nii.gz from BET output
```

### 3. FSL FLIRT Registration

**Required Data:**
- Input image to register
- Reference template image

**Test Data Setup:**
```bash
# Download MNI152 template
mkdir -p /Users/hp/Desktop/neurodesk/data/templates
wget http://www.bic.mni.mcgill.ca/~collins/brains/mni152_t1_tal_nlin_asym_09a.nii.gz \
     -O /Users/hp/Desktop/neurodesk/data/templates/MNI152_T1_2mm.nii.gz
```

**Example Usage:**
```bash
# Register brain-extracted image to MNI space
```

### 4. MRTrix3 FOD Estimation

**Required Data:**
- Diffusion-weighted imaging (DWI) data
- b-values file (.bval)
- b-vectors file (.bvec)
- Response function file (.txt)

**Test Data Sources:**
1. **Human Connectome Project** (best quality):
   - Download preprocessed DWI data
   - Includes bval/bvec files

2. **Create minimal test data**:
   ```bash
   # Create test DWI data directory
   mkdir -p /Users/hp/Desktop/neurodesk/data/diffusion

   # You'll need real DWI data for this tool to work properly
   # Synthetic DWI data is complex to create meaningfully
   ```

3. **Sample datasets**:
   - **MGH Adult Diffusion Dataset**: https://www.nmr.mgh.harvard.edu/
   - **Stanford HARDI dataset**: http://purl.stanford.edu/ng782rw8378

**Required files structure:**
```
diffusion/
├── dwi.nii.gz          # Diffusion-weighted images
├── dwi.bval            # b-values
├── dwi.bvec            # b-vectors
└── response.txt        # Response function (from dwi2response)
```

**Generate response function first:**
```bash
# You'll need to run dwi2response first to generate response.txt
# This requires real DWI data
```

### 5. FreeSurfer Cortical Reconstruction

**Required Data:**
- High-quality T1-weighted anatomical image
- Significant processing time (2-8 hours)

**Test Data:**
- Use same T1 data as for BET
- Ensure good image quality for FreeSurfer
- Minimum 1mm³ resolution recommended

**Example Usage:**
```bash
# This is a long-running process
# Use subject ID like "test_subject_01"
```

## Quick Start with Synthetic Data

For immediate testing, create synthetic data:

```python
# save as create_test_data.py
import numpy as np
import nibabel as nib
from pathlib import Path

def create_synthetic_t1():
    """Create synthetic T1-weighted image"""
    shape = (182, 218, 182)
    data = np.random.random(shape) * 1000

    # Create brain-like structure
    center = np.array(shape) // 2
    xx, yy, zz = np.meshgrid(*[np.arange(s) for s in shape])
    distance = np.sqrt((xx - center[0])**2 + (yy - center[1])**2 + (zz - center[2])**2)
    brain_mask = distance < 60
    data[~brain_mask] *= 0.1

    # Save
    img = nib.Nifti1Image(data.astype(np.float32), np.eye(4))
    output_path = Path('/Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(img, output_path)
    print(f"Created synthetic T1 image: {output_path}")

def create_mni_template():
    """Create simple MNI-like template"""
    shape = (182, 218, 182)
    data = np.random.random(shape) * 800 + 200  # Different intensity distribution

    img = nib.Nifti1Image(data.astype(np.float32), np.eye(4))
    output_path = Path('/Users/hp/Desktop/neurodesk/data/templates/synthetic_mni.nii.gz')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(img, output_path)
    print(f"Created synthetic MNI template: {output_path}")

if __name__ == "__main__":
    create_synthetic_t1()
    create_mni_template()
```

Run this to create test data:
```bash
cd /Users/hp/Desktop/neurodesk/data
python create_test_data.py
```

## Real Data Recommendations

### Best Quality Datasets:
1. **Human Connectome Project (HCP)**: Gold standard, preprocessed
2. **UK Biobank**: Large scale, population study
3. **ADNI**: Alzheimer's research, longitudinal
4. **OpenNeuro**: Open access, various studies

### Quick Access Datasets:
1. **IXI Dataset**: Healthy subjects, T1/T2/PD/MRA/DTI
2. **OASIS**: Cross-sectional and longitudinal
3. **ABIDE**: Autism research, resting-state fMRI + structural

## Testing Workflow

1. **Start with FSL BET**: Test brain extraction first
2. **Use BET output for FAST**: Tissue segmentation
3. **Download MNI template**: For registration testing
4. **Get real DWI data**: For diffusion analysis
5. **High-quality T1 for FreeSurfer**: Cortical reconstruction

## Data Format Requirements

- **Input formats**: NIfTI (.nii, .nii.gz), DICOM (converted to NIfTI)
- **Output formats**: NIfTI, MGZ (FreeSurfer), MIF (MRTrix3)
- **Coordinate systems**: Scanner coordinates, standard spaces (MNI, Talairach)

## Troubleshooting

### Common Issues:
1. **File permissions**: Ensure Docker can access data directories
2. **File paths**: Use absolute paths
3. **Image orientation**: Check image headers for proper orientation
4. **Memory requirements**: Large images may need more RAM

### Data Quality Checks:
```bash
# Check image properties
fslinfo /path/to/image.nii.gz

# View image (if FSL installed locally)
fsleyes /path/to/image.nii.gz
```