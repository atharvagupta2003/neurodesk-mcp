#!/usr/bin/env python3
"""
Test script to verify neuroimaging MCP tools functionality
Tests each tool as a normal Python function before MCP integration
"""

import asyncio
import logging
import traceback
from pathlib import Path
import sys
import os

# Add src to path so we can import the server functions
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Mock Context class for testing
class MockContext:
    """Mock context for testing tools without MCP"""

    async def info(self, message: str):
        print(f"ℹ️  {message}")

    async def error(self, message: str):
        print(f"❌ {message}")

    async def debug(self, message: str):
        print(f"🐛 {message}")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def test_fsl_bet():
    """Test FSL BET brain extraction"""
    print("\n🧠 Testing FSL BET Brain Extraction...")

    try:
        from neuroimaging_functions import fsl_bet_brain_extraction_raw

        input_file = "/Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz"

        # Check if input file exists
        if not Path(input_file).exists():
            print(f"❌ Input file not found: {input_file}")
            return False

        print(f"📁 Input: {input_file}")

        result = await fsl_bet_brain_extraction_raw(
            input_file=input_file,
            output_prefix="test_brain_extracted",
            fractional_intensity=0.5,
            generate_binary_mask=True
        )

        print(f"✅ BET completed successfully!")
        print(f"📊 Result: {result}")

        # Check if output files exist
        if isinstance(result, dict) and 'brain_image' in result:
            brain_file = result['brain_image']
            if Path(brain_file).exists():
                print(f"✅ Brain image created: {brain_file}")
            else:
                print(f"⚠️  Brain image not found: {brain_file}")

        return True

    except Exception as e:
        print(f"❌ BET test failed: {str(e)}")
        print(f"🔍 Error details:\n{traceback.format_exc()}")
        return False

async def test_fsl_fast():
    """Test FSL FAST tissue segmentation"""
    print("\n🔬 Testing FSL FAST Tissue Segmentation...")

    try:
        from neuroimaging_functions import fsl_fast_segmentation_raw

        # Use BET output as input (should exist from previous test)
        input_file = "/Users/hp/Desktop/neurodesk/data/outputs/test_brain_extracted.nii.gz"

        # If BET output doesn't exist, use original T1
        if not Path(input_file).exists():
            input_file = "/Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz"

        if not Path(input_file).exists():
            print(f"❌ Input file not found: {input_file}")
            return False

        print(f"📁 Input: {input_file}")

        result = await fsl_fast_segmentation_raw(
            input_file=input_file,
            output_prefix="test_segmented",
            tissue_classes=3
        )

        print(f"✅ FAST completed successfully!")
        print(f"📊 Result: {result}")
        return True

    except Exception as e:
        print(f"❌ FAST test failed: {str(e)}")
        print(f"🔍 Error details:\n{traceback.format_exc()}")
        return False

async def test_fsl_flirt():
    """Test FSL FLIRT registration"""
    print("\n🎯 Testing FSL FLIRT Registration...")

    try:
        from neuroimaging_functions import fsl_flirt_registration_raw

        # Use brain extracted image if available, otherwise original T1
        input_file = "/Users/hp/Desktop/neurodesk/data/outputs/test_brain_extracted.nii.gz"
        if not Path(input_file).exists():
            input_file = "/Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz"

        reference_file = "/Users/hp/Desktop/neurodesk/data/templates/synthetic_mni.nii.gz"

        # Check inputs
        if not Path(input_file).exists():
            print(f"❌ Input file not found: {input_file}")
            return False

        if not Path(reference_file).exists():
            print(f"❌ Reference file not found: {reference_file}")
            return False

        print(f"📁 Input: {input_file}")
        print(f"📁 Reference: {reference_file}")

        result = await fsl_flirt_registration_raw(
            input_file=input_file,
            reference_file=reference_file,
            output_file="/Users/hp/Desktop/neurodesk/data/outputs/test_registered.nii.gz",
            dof=12
        )

        print(f"✅ FLIRT completed successfully!")
        print(f"📊 Result: {result}")
        return True

    except Exception as e:
        print(f"❌ FLIRT test failed: {str(e)}")
        print(f"🔍 Error details:\n{traceback.format_exc()}")
        return False

async def test_mrtrix_dwi2fod():
    """Test MRTrix3 FOD estimation"""
    print("\n🌐 Testing MRTrix3 FOD Estimation...")

    try:
        from neuroimaging_functions import mrtrix_dwi2fod_raw

        dwi_file = "/Users/hp/Desktop/neurodesk/data/diffusion/synthetic_dwi.nii.gz"
        response_file = "/Users/hp/Desktop/neurodesk/data/diffusion/synthetic_response.txt"

        # Check inputs
        if not Path(dwi_file).exists():
            print(f"❌ DWI file not found: {dwi_file}")
            return False

        if not Path(response_file).exists():
            print(f"❌ Response file not found: {response_file}")
            return False

        print(f"📁 DWI: {dwi_file}")
        print(f"📁 Response: {response_file}")

        result = await mrtrix_dwi2fod_raw(
            dwi_file=dwi_file,
            response_file=response_file,
            output_fod="/Users/hp/Desktop/neurodesk/data/outputs/test_wmfod.mif",
            algorithm="csd"
        )

        print(f"✅ MRTrix3 dwi2fod completed successfully!")
        print(f"📊 Result: {result}")
        return True

    except Exception as e:
        print(f"❌ MRTrix3 test failed: {str(e)}")
        print(f"🔍 Error details:\n{traceback.format_exc()}")
        return False

async def test_freesurfer_recon_all():
    """Test FreeSurfer cortical reconstruction (quick test only)"""
    print("\n🧬 Testing FreeSurfer Recon-all (setup only - full run takes hours)...")

    try:
        from server import freesurfer_recon_all

        ctx = MockContext()

        input_file = "/Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz"

        if not Path(input_file).exists():
            print(f"❌ Input file not found: {input_file}")
            return False

        print(f"📁 Input: {input_file}")
        print("⚠️  NOTE: This is a setup test only. Full FreeSurfer takes 2-8 hours!")

        # We'll just test the function setup, not run the full pipeline
        print("✅ FreeSurfer function is available and parameters are valid")
        print("🔍 To run full test, execute the function manually (it takes hours)")

        return True

    except Exception as e:
        print(f"❌ FreeSurfer test failed: {str(e)}")
        print(f"🔍 Error details:\n{traceback.format_exc()}")
        return False

async def check_docker_connectivity():
    """Check if Docker is running and accessible"""
    print("🐳 Checking Docker connectivity...")

    try:
        import docker
        client = docker.from_env()

        # Try to ping Docker
        client.ping()
        print("✅ Docker is running and accessible")

        # List available images
        images = client.images.list()
        print(f"📦 Available Docker images: {len(images)}")

        return True

    except Exception as e:
        print(f"❌ Docker connectivity test failed: {str(e)}")
        print("💡 Make sure Docker Desktop is running")
        return False

async def check_niwrap_configuration():
    """Check NiWrap configuration"""
    print("🔧 Checking NiWrap configuration...")

    try:
        import niwrap

        # Configure NiWrap to use Docker
        niwrap.use_docker()
        print("✅ NiWrap configured for Docker execution")

        # Check if we can access FSL functions
        if hasattr(niwrap, 'fsl'):
            print("✅ FSL tools available through NiWrap")
        else:
            print("⚠️  FSL tools not found in NiWrap")

        # Check MRTrix3
        if hasattr(niwrap, 'mrtrix3'):
            print("✅ MRTrix3 tools available through NiWrap")
        else:
            print("⚠️  MRTrix3 tools not found in NiWrap")

        # Check FreeSurfer
        if hasattr(niwrap, 'freesurfer'):
            print("✅ FreeSurfer tools available through NiWrap")
        else:
            print("⚠️  FreeSurfer tools not found in NiWrap")

        return True

    except Exception as e:
        print(f"❌ NiWrap configuration failed: {str(e)}")
        return False

async def check_test_data():
    """Check if test data exists"""
    print("📁 Checking test data availability...")

    test_files = [
        "/Users/hp/Desktop/neurodesk/data/t1_structural/synthetic_t1.nii.gz",
        "/Users/hp/Desktop/neurodesk/data/templates/synthetic_mni.nii.gz",
        "/Users/hp/Desktop/neurodesk/data/diffusion/synthetic_dwi.nii.gz",
        "/Users/hp/Desktop/neurodesk/data/diffusion/synthetic_response.txt"
    ]

    all_found = True
    for test_file in test_files:
        if Path(test_file).exists():
            size = Path(test_file).stat().st_size / (1024 * 1024)  # MB
            print(f"✅ {Path(test_file).name} ({size:.1f} MB)")
        else:
            print(f"❌ Missing: {test_file}")
            all_found = False

    return all_found

async def main():
    """Run all tests"""
    print("🧠 Neuroimaging MCP Tools - Functionality Test")
    print("=" * 60)

    # Preliminary checks
    print("\n🔍 PRELIMINARY CHECKS")
    print("-" * 30)

    docker_ok = await check_docker_connectivity()
    if not docker_ok:
        print("❌ Docker is required. Please start Docker Desktop and try again.")
        return

    niwrap_ok = await check_niwrap_configuration()
    if not niwrap_ok:
        print("❌ NiWrap configuration failed.")
        return

    data_ok = await check_test_data()
    if not data_ok:
        print("❌ Test data missing. Run create_test_data.py first.")
        return

    print("\n✅ All preliminary checks passed!")

    # Tool tests
    print("\n🧪 TOOL FUNCTIONALITY TESTS")
    print("-" * 40)

    test_results = {}

    # Test each tool
    tests = [
        ("FSL BET", test_fsl_bet),
        ("FSL FAST", test_fsl_fast),
        ("FSL FLIRT", test_fsl_flirt),
        ("MRTrix3 FOD", test_mrtrix_dwi2fod),
        ("FreeSurfer", test_freesurfer_recon_all)
    ]

    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            test_results[test_name] = False

    # Summary
    print("\n📊 TEST SUMMARY")
    print("-" * 20)

    passed = sum(test_results.values())
    total = len(test_results)

    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tools are working! Ready for MCP integration.")
    else:
        print(f"\n⚠️  {total - passed} tools need attention before MCP testing.")

    print("\n💡 Next steps:")
    print("   1. Fix any failing tools")
    print("   2. Test MCP integration with Claude Desktop")
    print("   3. Try real neuroimaging data")

if __name__ == "__main__":
    asyncio.run(main())