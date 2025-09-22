#!/usr/bin/env python3
"""
Test MCP integration without requiring Docker containers
Tests that tools are properly exposed through MCP protocol
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server_startup():
    """Test that MCP server starts up properly"""
    print("🚀 Testing MCP Server Startup...")

    try:
        # Start server process
        proc = subprocess.Popen(
            ["uv", "run", "python", "src/server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )

        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        # Send request
        init_json = json.dumps(init_request) + "\n"
        proc.stdin.write(init_json)
        proc.stdin.flush()

        # Read response (with timeout)
        try:
            stdout, stderr = proc.communicate(timeout=10)

            if "Neuroimaging MCP Server" in stderr:
                print("✅ MCP Server started successfully")

                # Try to parse any JSON responses
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get("method") == "initialized":
                                print("✅ MCP initialization successful")
                        except json.JSONDecodeError:
                            pass

                return True
            else:
                print(f"❌ Unexpected server response: {stderr}")
                return False

        except subprocess.TimeoutExpired:
            proc.kill()
            print("❌ Server startup timed out")
            return False

    except Exception as e:
        print(f"❌ Server startup failed: {str(e)}")
        return False

async def test_mcp_tools_list():
    """Test that tools are properly exposed"""
    print("\n🛠️  Testing MCP Tools List...")

    try:
        # Start server
        proc = subprocess.Popen(
            ["uv", "run", "python", "src/server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )

        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }

        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }

        # Tools list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }

        # Send all requests
        requests = [
            json.dumps(init_request),
            json.dumps(initialized_notification),
            json.dumps(tools_request)
        ]

        input_data = "\n".join(requests) + "\n"

        try:
            stdout, stderr = proc.communicate(input=input_data, timeout=15)

            # Parse responses
            lines = stdout.strip().split('\n')
            tools_found = []

            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get("id") == 2 and "result" in response:
                            tools = response["result"].get("tools", [])
                            for tool in tools:
                                tools_found.append(tool.get("name"))
                    except json.JSONDecodeError:
                        continue

            expected_tools = [
                "fsl_bet_brain_extraction",
                "fsl_fast_segmentation",
                "fsl_flirt_registration",
                "mrtrix_dwi2fod",
                "freesurfer_recon_all"
            ]

            print(f"📋 Found tools: {tools_found}")

            for tool in expected_tools:
                if tool in tools_found:
                    print(f"✅ {tool}")
                else:
                    print(f"❌ {tool} - NOT FOUND")

            success_count = sum(1 for tool in expected_tools if tool in tools_found)
            print(f"\n📊 Tools test: {success_count}/{len(expected_tools)} tools found")

            return success_count == len(expected_tools)

        except subprocess.TimeoutExpired:
            proc.kill()
            print("❌ Tools list request timed out")
            return False

    except Exception as e:
        print(f"❌ Tools list test failed: {str(e)}")
        return False

async def test_mcp_resources():
    """Test that resources are exposed"""
    print("\n📚 Testing MCP Resources...")

    try:
        proc = subprocess.Popen(
            ["uv", "run", "python", "src/server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )

        # Initialize and request resources
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"resources": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }

        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }

        resources_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "resources/list"
        }

        requests = [
            json.dumps(init_request),
            json.dumps(initialized_notification),
            json.dumps(resources_request)
        ]

        input_data = "\n".join(requests) + "\n"

        try:
            stdout, stderr = proc.communicate(input=input_data, timeout=10)

            lines = stdout.strip().split('\n')
            resources_found = []

            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get("id") == 2 and "result" in response:
                            resources = response["result"].get("resources", [])
                            for resource in resources:
                                resources_found.append(resource.get("uri"))
                    except json.JSONDecodeError:
                        continue

            print(f"📋 Found resources: {resources_found}")

            if "neuroimaging://workspace/{session_id}" in resources_found:
                print("✅ Workspace resource found")
                return True
            else:
                print("❌ Workspace resource not found")
                return False

        except subprocess.TimeoutExpired:
            proc.kill()
            print("❌ Resources request timed out")
            return False

    except Exception as e:
        print(f"❌ Resources test failed: {str(e)}")
        return False

async def test_data_availability():
    """Test that test data is available"""
    print("\n📁 Testing Data Availability...")

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
    """Run all MCP integration tests"""
    print("🧠 Neuroimaging MCP - Integration Test (No Docker Required)")
    print("=" * 65)

    tests = [
        ("Data Availability", test_data_availability),
        ("MCP Server Startup", test_mcp_server_startup),
        ("MCP Tools List", test_mcp_tools_list),
        ("MCP Resources", test_mcp_resources)
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} crashed: {str(e)}")
            results[test_name] = False

    # Summary
    print("\n📊 INTEGRATION TEST SUMMARY")
    print("-" * 35)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All MCP integration tests passed!")
        print("✅ MCP server is ready for use with Claude Desktop")
        print("\n💡 Next steps:")
        print("   1. Configure Claude Desktop with the MCP server")
        print("   2. Test with real neuroimaging data")
        print("   3. Ensure adequate disk space for Docker containers")
    else:
        print(f"\n⚠️  {total - passed} tests failed - MCP integration needs work")
        print("\n🔧 Debugging steps:")
        print("   1. Check FastMCP installation")
        print("   2. Verify server.py syntax")
        print("   3. Review MCP protocol implementation")

if __name__ == "__main__":
    asyncio.run(main())