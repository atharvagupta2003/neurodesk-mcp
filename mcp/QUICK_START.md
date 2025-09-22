# Quick Start Guide - Neuroimaging MCP Server

## ✅ Setup Complete!

Your neuroimaging MCP server is now ready to use with 5 core tools and synthetic test data.

**✓ Server Status**: Running successfully with FastMCP 2.12.3 and MCP SDK 1.14.1

## 🧠 Available Tools

1. **FSL BET Brain Extraction** - `fsl_bet_brain_extraction`
2. **FSL FAST Tissue Segmentation** - `fsl_fast_segmentation`
3. **FSL FLIRT Registration** - `fsl_flirt_registration`
4. **MRTrix3 FOD Estimation** - `mrtrix_dwi2fod`
5. **FreeSurfer Cortical Reconstruction** - `freesurfer_recon_all`

## 🗂️ Test Data Created

### Synthetic Data Locations:
- **T1 Structural**: `/Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz`
- **MNI Template**: `/Users/hp/Desktop/neurodesk/data/templates/synthetic_mni.nii.gz`
- **DWI Data**: `/Users/hp/Desktop/neurodesk/data/diffusion/synthetic_dwi.nii.gz`
- **Response Function**: `/Users/hp/Desktop/neurodesk/data/diffusion/synthetic_response.txt`

## 🚀 Testing Each Tool

### 1. Test FSL BET Brain Extraction

**Test Data**: Use the synthetic T1 image
```bash
# Input: /Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz
# Output: /Users/hp/Desktop/neurodesk/data/outputs/brain_extracted.nii.gz
```

**Example prompt for Claude:**
```
"Please extract the brain from the T1 image at /Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz using a fractional intensity of 0.5"
```

### 2. Test FSL FAST Tissue Segmentation

**Test Data**: Use output from BET (brain_extracted.nii.gz)
```bash
# Input: /Users/hp/Desktop/neurodesk/data/outputs/brain_extracted.nii.gz
# Output: /Users/hp/Desktop/neurodesk/data/outputs/segmented_*
```

**Example prompt:**
```
"Please segment the brain-extracted image into tissue types using FSL FAST"
```

### 3. Test FSL FLIRT Registration

**Test Data**: Brain image + MNI template
```bash
# Input: /Users/hp/Desktop/neurodesk/data/outputs/brain_extracted.nii.gz
# Reference: /Users/hp/Desktop/neurodesk/data/templates/synthetic_mni.nii.gz
# Output: /Users/hp/Desktop/neurodesk/data/outputs/registered.nii.gz
```

**Example prompt:**
```
"Register the brain-extracted image to MNI space using the template at /Users/hp/Desktop/neurodesk/data/templates/synthetic_mni.nii.gz"
```

### 4. Test MRTrix3 FOD Estimation

**Test Data**: Diffusion data with response function
```bash
# DWI: /Users/hp/Desktop/neurodesk/data/diffusion/synthetic_dwi.nii.gz
# Response: /Users/hp/Desktop/neurodesk/data/diffusion/synthetic_response.txt
# Output: /Users/hp/Desktop/neurodesk/data/outputs/wmfod.mif
```

**Example prompt:**
```
"Estimate fiber orientation distributions from the DWI data at /Users/hp/Desktop/neurodesk/data/diffusion/synthetic_dwi.nii.gz using the response function"
```

### 5. Test FreeSurfer Cortical Reconstruction

**Test Data**: High-quality T1 image
```bash
# Input: /Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz
# Subject ID: test_subject_01
# Output: /Users/hp/Desktop/neurodesk/data/freesurfer_subjects/test_subject_01/
```

**Example prompt:**
```
"Run FreeSurfer cortical reconstruction on the T1 image for subject 'test_subject_01'"
```

**Note**: FreeSurfer takes 2-8 hours to complete!

## 🔧 Running the Server

### Start the Server:
```bash
cd /Users/hp/Desktop/neurodesk/mcp
uv run python src/server.py
```

### Configure with Claude Desktop:
Add to `~/.config/claude-desktop/mcp_servers.json`:
```json
{
  "mcpServers": {
    "neuroimaging": {
      "command": "uv",
      "args": ["run", "python", "/Users/hp/Desktop/neurodesk/mcp/src/server.py"],
      "cwd": "/Users/hp/Desktop/neurodesk/mcp",
      "env": {
        "DOCKER_HOST": "unix:///var/run/docker.sock"
      }
    }
  }
}
```

## 📁 Directory Structure

```
/Users/hp/Desktop/neurodesk/
├── mcp/                           # MCP Server
│   ├── src/server.py             # Main server code
│   ├── pyproject.toml            # Dependencies (uv)
│   ├── README.md                 # Full documentation
│   └── QUICK_START.md            # This file
└── data/                         # Test data
    ├── t1_structural/            # T1-weighted images
    ├── diffusion/               # DWI data
    ├── templates/               # Reference templates
    ├── freesurfer_subjects/     # FreeSurfer outputs
    ├── outputs/                 # Tool outputs
    ├── TEST_DATA_GUIDE.md       # Detailed data guide
    └── create_test_data.py      # Test data generator
```

## 🐳 Docker Requirements

Make sure Docker is running for NiWrap container execution:
```bash
docker --version
docker ps  # Should work without errors
```

The following containers will be pulled automatically:
- `brainlife/fsl:6.0.4` (FSL tools)
- `mrtrix3/mrtrix3:3.0.4` (MRTrix3 tools)
- `freesurfer/freesurfer:7.4.1` (FreeSurfer)

## 🎯 Quick Test Workflow

1. **Start with brain extraction** - safest first test
2. **Use BET output for segmentation** - tests tool chaining
3. **Register to template** - tests reference data usage
4. **Try diffusion analysis** - tests complex data
5. **FreeSurfer last** - longest running process

## 📚 Getting Real Data

For production use, replace synthetic data with real neuroimaging data:

### Recommended Sources:
- **OpenNeuro**: https://openneuro.org (open datasets)
- **Human Connectome Project**: https://db.humanconnectome.org
- **UK Biobank**: https://www.ukbiobank.ac.uk
- **OASIS**: https://www.oasis-brains.org

### File Formats:
- **Input**: NIfTI (.nii.gz), DICOM (convert to NIfTI)
- **Output**: NIfTI, MGZ, MIF formats

## 🚨 Troubleshooting

### Common Issues:
1. **Docker not running**: Start Docker Desktop
2. **File permissions**: Ensure Docker can access data directories
3. **Memory issues**: Large images need 8GB+ RAM
4. **Container pulls**: First run may take time downloading containers

### Check logs:
```bash
# Server logs show in terminal
# Check Docker containers:
docker ps
docker logs <container_id>
```

## 🎉 Next Steps

1. **Test with real data**: Replace synthetic data with actual neuroimaging files
2. **Add more tools**: Extend server with additional neuroimaging functions
3. **Create workflows**: Chain multiple tools for complete analysis pipelines
4. **Deploy**: Set up for production use with proper authentication

Your neuroimaging MCP server is ready to bridge AI and brain imaging! 🧠🤖