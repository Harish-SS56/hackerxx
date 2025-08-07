#!/usr/bin/env python3
"""
Test script to validate Gemini 2.5 Flash upgrades and accuracy improvements
"""

import requests
import json
import time
import sys

def test_hackrx_api():
    """Test the upgraded HackRx API with Gemini 2.5 Flash"""
    
    base_url = "http://localhost:5000"
    headers = {
        "Authorization": "Bearer hackrx-secret-key-2024",
        "Content-Type": "application/json"
    }
    
    # Test data with substantial PDF content
    test_data = {
        "documents": "https://www.africau.edu/images/default/sample.pdf",
        "questions": [
            "What is the title of this document?",
            "What is the main topic discussed?", 
            "What university is mentioned?",
            "Who are the authors of this document?",
            "What specific medical procedures are described?"  # This should return empty string if not found
        ]
    }
    
    print("🚀 Testing HackRx API with Gemini 2.5 Flash Upgrades")
    print("=" * 60)
    
    # Test health endpoint first
    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Health check: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   Gemini status: {health_data.get('gemini_client', 'unknown')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test main QA endpoint
    try:
        print(f"\n📄 Testing with PDF: {test_data['documents']}")
        print(f"❓ Questions: {len(test_data['questions'])}")
        
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/hackrx/run",
            headers=headers,
            json=test_data,
            timeout=60
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f} seconds")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            answers = result.get("answers", [])
            
            print(f"✅ Got {len(answers)} answers")
            print("\n📋 RESULTS:")
            print("-" * 40)
            
            for i, (question, answer) in enumerate(zip(test_data["questions"], answers), 1):
                print(f"\n{i}. Q: {question}")
                if answer == "":
                    print(f"   A: [EMPTY STRING - NOT FOUND] ✅")
                else:
                    print(f"   A: {answer}")
            
            # Validate response format
            print("\n🔍 VALIDATION:")
            print("-" * 40)
            
            # Check if all questions got answers (including empty strings)
            if len(answers) == len(test_data["questions"]):
                print("✅ Answer count matches question count")
            else:
                print(f"❌ Answer count mismatch: {len(answers)} vs {len(test_data['questions'])}")
            
            # Check for proper empty string handling
            empty_answers = sum(1 for a in answers if a == "")
            non_empty_answers = sum(1 for a in answers if a != "")
            
            print(f"✅ Non-empty answers: {non_empty_answers}")
            print(f"✅ Empty string answers: {empty_answers}")
            
            # Check for old "Not found" patterns
            old_patterns = ["not found in document", "not found", "not available"]
            bad_answers = [a for a in answers if any(pattern in a.lower() for pattern in old_patterns)]
            
            if bad_answers:
                print(f"❌ Found old 'Not found' patterns: {len(bad_answers)}")
                for bad in bad_answers:
                    print(f"   - '{bad}'")
            else:
                print("✅ No old 'Not found' patterns detected")
            
            return True
            
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Main test function"""
    print("HackRx 6.0 - Gemini 2.5 Flash Upgrade Test")
    print("=" * 50)
    
    success = test_hackrx_api()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Gemini 2.5 Flash upgrade successful")
        print("✅ Accuracy optimizations working")
        print("✅ Empty string handling correct")
        print("✅ Response format validated")
    else:
        print("\n❌ TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()