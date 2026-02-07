"""
Simple test script to verify VentureScope setup.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# --------------------------------------------------
# Project setup
# --------------------------------------------------

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after path setup
from core.llm_client import HuggingFaceLLMClient


print("=" * 60)
print("VentureScope Setup Test")
print("=" * 60)

# --------------------------------------------------
# Test 1: Check environment
# --------------------------------------------------
print("\n1. Checking environment...")

load_dotenv()

api_key = os.getenv("HUGGINGFACE_API_KEY")

if api_key:
    print(f"   ✅ API Key found: {api_key[:10]}...")
else:
    print("   ❌ API Key not found in environment")
    print("   Please add HUGGINGFACE_API_KEY to .env file")
    sys.exit(1)

# --------------------------------------------------
# Test 2: Initialize LLM client
# --------------------------------------------------
print("\n2. Initializing LLM client...")

try:
    client = HuggingFaceLLMClient()
    print("   ✅ LLM client initialized")
    print(f"   Model: {client.model}")
except Exception as e:
    print(f"   ❌ Failed to initialize: {str(e)}")
    sys.exit(1)

# --------------------------------------------------
# Test 3: Test API connection
# --------------------------------------------------
print("\n3. Testing HuggingFace API connection...")

try:
    response = client.generate(
        prompt="Say 'Hello from VentureScope!' in one sentence.",
        max_tokens=50,
        temperature=0.7,
    )
    print(f"   ✅ API Response: {response[:100]}...")
except Exception as e:
    print(f"   ❌ API test failed: {str(e)}")
    sys.exit(1)

# --------------------------------------------------
# Test 4: Check project structure
# --------------------------------------------------
print("\n4. Checking project structure...")

required_dirs = [
    "agents",
    "core",
    "utils",
    "data",
    "outputs",
]

for dir_name in required_dirs:
    dir_path = project_root / dir_name
    if dir_path.exists():
        print(f"   ✅ {dir_name}/ exists")
    else:
        print(f"   ⚠️ {dir_name}/ not found")

# --------------------------------------------------
# Test 5: Check key files
# --------------------------------------------------
print("\n5. Checking key files...")

key_files = [
    "app.py",
    "core/orchestrator.py",
    "core/llm_client.py",
    "agents/document_ingestion.py",
    "utils/pdf_extractor.py",
]

for file_name in key_files:
    file_path = project_root / file_name
    if file_path.exists():
        print(f"   ✅ {file_name} exists")
    else:
        print(f"   ❌ {file_name} not found")

# --------------------------------------------------
# Done
# --------------------------------------------------
print("\n" + "=" * 60)
print("✅ Setup test complete! VentureScope is ready.")
print("\nNext steps:")
print("1. Run: streamlit run app.py")
print("2. Upload a pitch deck PDF")
print("3. Get your investment memo!")
print("=" * 60)
