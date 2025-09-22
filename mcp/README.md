# Neuroimaging MCP Server

A FastMCP server that provides neuroimaging analysis tools through the Model Context Protocol. This server integrates with NiWrap for containerized execution of neuroimaging software packages.

## Features

This MCP server provides 5 core neuroimaging tools:

1. **FSL BET Brain Extraction** - Extract brain from skull using FSL BET
2. **FSL FAST Tissue Segmentation** - Segment brain tissue into GM/WM/CSF
3. **FSL FLIRT Registration** - Linear registration to reference space
4. **MRTrix3 FOD Estimation** - Fiber orientation distribution estimation for diffusion MRI
5. **FreeSurfer Cortical Reconstruction** - Complete cortical surface reconstruction

## Installation

### Prerequisites

- Python 3.10+
- Docker (for containerized neuroimaging tools)
- [uv](https://docs.astral.sh/uv/) (recommended package manager)

### Setup

1. Clone or navigate to the project directory:
   ```bash
   cd /Users/hp/Desktop/neurodesk/mcp
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

## Usage

### Running the Server

Start the MCP server using FastMCP:

```bash
# Using the entry point
neuroimaging-mcp

# Or run directly
python src/server.py
```

The server runs on STDIO transport by default, making it compatible with MCP clients like Claude Desktop.

### Available Tools

#### 1. Brain Extraction (FSL BET)
```python
fsl_bet_brain_extraction(
    input_file: str,
    output_prefix: str = "brain_extracted",
    fractional_intensity: float = 0.5,
    generate_binary_mask: bool = True
)
```

#### 2. Tissue Segmentation (FSL FAST)
```python
fsl_fast_segmentation(
    input_file: str,
    output_prefix: str = "segmented",
    tissue_classes: int = 3
)
```

#### 3. Linear Registration (FSL FLIRT)
```python
fsl_flirt_registration(
    input_file: str,
    reference_file: str,
    output_file: str = "registered.nii.gz",
    dof: int = 12
)
```

#### 4. FOD Estimation (MRTrix3)
```python
mrtrix_dwi2fod(
    dwi_file: str,
    response_file: str,
    output_fod: str = "wmfod.mif",
    algorithm: str = "csd"
)
```

#### 5. Cortical Reconstruction (FreeSurfer)
```python
freesurfer_recon_all(
    input_file: str,
    subject_id: str,
    subjects_dir: str = "/tmp/freesurfer_subjects"
)
```

### Resources

The server provides workspace information through resources:

- `neuroimaging://workspace/{session_id}` - Get information about workspace files

### Prompts

Available analysis guidance prompts:

- `neuroimaging_analysis_guide(analysis_type)` - Get guidance for different analysis types
  - `analysis_type`: "brain_extraction", "preprocessing", "diffusion"

## Example Usage with Claude

Once the server is running, you can interact with it through Claude Desktop or other MCP clients:

```
"Please extract the brain from my T1 MRI scan located at /data/T1w.nii.gz using a conservative fractional intensity of 0.4"

"I need to run a complete preprocessing pipeline on my brain image. First extract the brain, then segment tissues, and finally register to MNI space."

"Estimate fiber orientation distributions from my diffusion data at /data/dwi.nii.gz using the response function at /data/response.txt"
```

## Configuration for Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "neuroimaging": {
      "command": "python",
      "args": ["/Users/hp/Desktop/neurodesk/mcp/src/server.py"],
      "env": {
        "DOCKER_HOST": "unix:///var/run/docker.sock"
      }
    }
  }
}
```

## Development

### Project Structure

```
mcp/
├── src/
│   └── server.py          # Main MCP server implementation
├── pyproject.toml         # Project configuration with uv
├── README.md             # This file
└── .venv/                # Virtual environment (created by uv)
```

### Dependencies

- **fastmcp**: FastMCP framework for building MCP servers
- **niwrap**: Python wrappers for neuroimaging tools
- **docker**: Container management for neuroimaging software
- **nibabel**: Neuroimaging file I/O
- **numpy**: Numerical computing

### Testing

```bash
# Install dev dependencies
uv sync --dev

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
black src/

# Sort imports
isort src/

# Type checking
mypy src/
```

## Docker Containers

The server uses the following Docker containers through NiWrap:

- **FSL**: `brainlife/fsl:6.0.4`
- **MRTrix3**: `mrtrix3/mrtrix3:3.0.4`
- **FreeSurfer**: `freesurfer/freesurfer:7.4.1`

These will be automatically pulled when first used.

## Supported File Formats

- **Input**: NIfTI (.nii, .nii.gz), MGZ (.mgz), MIF (.mif)
- **Output**: NIfTI, MGZ, MIF, and various neuroimaging formats

## Troubleshooting

### Docker Issues

1. Ensure Docker is running and accessible
2. Check user permissions for Docker socket
3. Pre-pull containers: `docker pull brainlife/fsl:6.0.4`

### File Path Issues

- Use absolute paths for input files
- Ensure proper file permissions
- Check that input files exist and are readable

### Memory Issues

Large neuroimaging datasets may require significant memory. Monitor system resources and adjust Docker memory limits if needed.

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## Support

For issues related to:
- **MCP functionality**: Check FastMCP documentation
- **Neuroimaging tools**: Refer to NiWrap documentation
- **Container issues**: Check Docker configuration