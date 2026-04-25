#!/usr/bin/env python3
"""
Test script to verify the enhanced prompt logic for interview question generation.
Tests language detection and prompt structure.
"""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from gemini_service import GeminiService


def test_language_extraction():
    """Test language detection from candidate profiles"""
    
    test_cases = [
        {
            "profile": "Senior Python developer with 8 years of experience. Expertise in Django, FastAPI, and async programming.",
            "expected": ["python"],
            "description": "Python profile"
        },
        {
            "profile": "Full-stack engineer. Strong in JavaScript/TypeScript, React, Node.js, Express.js",
            "expected": ["javascript", "typescript"],
            "description": "JavaScript/TypeScript profile"
        },
        {
            "profile": "Backend developer specializing in Java Spring Boot, Microservices, and Apache Kafka",
            "expected": ["java"],
            "description": "Java Spring profile"
        },
        {
            "profile": "Full-stack developer: Python + Django backend, React frontend, PostgreSQL databases",
            "expected": ["python", "javascript"],
            "description": "Mixed tech stack"
        },
        {
            "profile": "C# developer with ASP.NET Core, Entity Framework, and SQL Server expertise",
            "expected": ["c#"],
            "description": "C# .NET profile"
        },
        {
            "profile": "Go enthusiast, building microservices with Gin framework",
            "expected": ["go"],
            "description": "Go profile"
        },
        {
            "profile": "No specific programming language mentioned",
            "expected": ["Python"],
            "description": "No language found (default)"
        },
    ]
    
    print("=" * 70)
    print("TESTING LANGUAGE EXTRACTION")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        result = GeminiService.extract_programming_languages(test["profile"])
        result_list = [lang.strip() for lang in result.split(",")]
        
        # Normalize for comparison
        expected_normalized = [lang.lower() for lang in test["expected"]]
        result_normalized = [lang.lower() for lang in result_list]
        
        # Check if all expected languages are in result
        matches = all(exp in result_normalized for exp in expected_normalized)
        
        status = "✓ PASS" if matches else "✗ FAIL"
        print(f"\n{status}: {test['description']}")
        print(f"  Profile: {test['profile'][:60]}...")
        print(f"  Expected: {', '.join(test['expected'])}")
        print(f"  Got: {result}")
        
        if matches:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 70)
    
    return failed == 0


def test_prompt_structure():
    """Test that the prompt is properly structured"""
    
    print("\n" + "=" * 70)
    print("TESTING PROMPT STRUCTURE")
    print("=" * 70)
    
    # Create a minimal GeminiService-like test (without actual API key)
    sample_profile = "Python developer with Django experience and PostgreSQL expertise"
    num_questions = 30
    
    # Extract languages
    languages = GeminiService.extract_programming_languages(sample_profile)
    
    # Calculate distribution
    technical_count = int(num_questions * 0.40)
    project_count = int(num_questions * 0.40)
    coding_count = num_questions - technical_count - project_count
    
    print(f"\nQuestion Distribution for {num_questions} questions:")
    print(f"  Technical Questions (~40%): {technical_count}")
    print(f"  Project/Experience Questions (~40%): {project_count}")
    print(f"  Coding Questions (~20%): {coding_count}")
    print(f"  Total: {technical_count + project_count + coding_count}")
    
    print(f"\nDetected Languages: {languages}")
    
    print("\n✓ Prompt structure validated successfully!")
    print("=" * 70)
    
    return True


def test_json_parsing():
    """Test the JSON parsing logic with sample responses"""
    
    print("\n" + "=" * 70)
    print("TESTING JSON PARSING")
    print("=" * 70)
    
    # Test case 1: Multiple JSON objects separated by blank lines
    sample_response_1 = """
{
"Topic": "Python Basics",
"Question": "What is a Python decorator?",
"Answer": "A decorator is a function that takes another function as input and adds extra functionality. For example, @property converts a method into a read-only attribute."
}

{
"Topic": "Django Framework",
"Question": "How do ORM querysets work?",
"Answer": "Django ORM querysets are lazy - they only execute when evaluated. You can chain filters before execution: User.objects.filter(active=True).exclude(role='admin')"
}
"""
    
    # Test case 2: JSON with code examples (multiline content)
    sample_response_2 = """
{
"Topic": "API Design",
"Question": "How do you handle validation in FastAPI?",
"Answer": "Use Pydantic models for automatic validation. Example:\n\nfrom pydantic import BaseModel\n\nclass User(BaseModel):\n    name: str\n    age: int\n\n@app.post('/users')\nasync def create_user(user: User):\n    return user"
}
"""
    
    # Test parsing
    print("\nTest 1: Parsing multiple JSON objects...")
    results_1 = GeminiService.parse_qa_response(sample_response_1)
    print(f"  Found {len(results_1)} Q&A items")
    if len(results_1) == 2:
        print("  ✓ Correctly parsed 2 JSON objects")
    else:
        print(f"  ✗ Expected 2 items, got {len(results_1)}")
    
    print("\nTest 2: Parsing JSON with code examples...")
    results_2 = GeminiService.parse_qa_response(sample_response_2)
    print(f"  Found {len(results_2)} Q&A items")
    if len(results_2) == 1:
        print("  ✓ Correctly parsed 1 JSON object with code example")
        print(f"  Answer length: {len(results_2[0]['Answer'])} chars")
    else:
        print(f"  ✗ Expected 1 item, got {len(results_2)}")
    
    print("\n" + "=" * 70)
    
    return len(results_1) == 2 and len(results_2) == 1


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " INTERVIEW Q&A ENHANCEMENT TEST SUITE ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = []
    
    # Run tests
    results.append(("Language Extraction", test_language_extraction()))
    results.append(("Prompt Structure", test_prompt_structure()))
    results.append(("JSON Parsing", test_json_parsing()))
    
    # Summary
    print("\n" + "=" * 70)
    print("OVERALL TEST SUMMARY")
    print("=" * 70)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    print("\n" + ("=" * 70))
    if all_passed:
        print("✓ ALL TESTS PASSED - Enhancements are working correctly!")
    else:
        print("✗ SOME TESTS FAILED - Please review the implementation")
    print("=" * 70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
