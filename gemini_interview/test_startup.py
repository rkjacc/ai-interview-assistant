#!/usr/bin/env python3
"""Test backend startup to verify all imports and initialization work"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("[TEST] Testing backend startup...")
print()

# Test imports
print("[1/3] Testing imports...")
try:
    from backend.models import InterviewRequest, InterviewResponse
    print("      [OK] Models imported")
except Exception as e:
    print(f"      [ERROR] Failed to import models: {e}")
    sys.exit(1)

try:
    from backend.gemini_service import GeminiService
    print("      [OK] GeminiService imported")
except Exception as e:
    print(f"      [ERROR] Failed to import GeminiService: {e}")
    sys.exit(1)

try:
    from backend.main import app
    print("      [OK] FastAPI app imported")
except Exception as e:
    print(f"      [ERROR] Failed to import FastAPI app: {e}")
    sys.exit(1)

# Test API structure
print()
print("[2/3] Testing API structure...")
routes = [route.path for route in app.routes]
print(f"      Found {len(routes)} routes:")
for route in routes:
    print(f"      - {route}")

# Test service initialization
print()
print("[3/3] Testing service initialization...")
try:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        secret_file = Path(__file__).parent.parent / "secret_api_key.txt"
        if secret_file.exists():
            api_key = GeminiService.get_api_key_from_file(str(secret_file))
    
    if api_key:
        service = GeminiService(api_key)
        print("      [OK] GeminiService initialized with API key")
    else:
        print("      [INFO] No API key - demo mode will be used")
        service = None
except Exception as e:
    print(f"      [ERROR] Failed to initialize service: {e}")
    sys.exit(1)

print()
print("[SUCCESS] All tests passed! Backend is ready to run.")
print()
print("To start the backend, run:")
print("  python backend/main.py")
print()
print("Or to use uvicorn:")
print("  python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001")
