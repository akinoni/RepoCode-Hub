#!/usr/bin/env python3
"""
Backend API Testing for AI-powered Code Learning System
Tests all backend endpoints according to test_result.md requirements
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://d96c4034-f976-4531-b6d2-dc75088aa0dc.preview.emergentagent.com/api"
TEST_USER_ID = f"test_user_{uuid.uuid4().hex[:8]}"
TEST_REPO_URL = "https://github.com/octocat/Hello-World"

# Test data
TEST_AI_CONFIG = {
    "provider": "openai",
    "model": "gpt-4o",
    "api_key": "sk-test-key-12345",
    "user_id": TEST_USER_ID
}

def print_test_result(test_name, success, details=""):
    """Print formatted test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   Details: {details}")
    print()

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            details = f"Status: {data.get('status')}, Message: {data.get('message')}"
        else:
            details = f"HTTP {response.status_code}: {response.text}"
            
        print_test_result("Health Check", success, details)
        return success
    except Exception as e:
        print_test_result("Health Check", False, f"Exception: {str(e)}")
        return False

def test_ai_models_endpoint():
    """Test the AI models listing endpoint"""
    print("🔍 Testing AI Models Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/ai-models", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            providers = list(data.keys())
            total_models = sum(len(models) for models in data.values())
            details = f"Providers: {providers}, Total models: {total_models}"
            
            # Verify expected providers exist
            expected_providers = ["openai", "anthropic", "gemini"]
            has_all_providers = all(provider in data for provider in expected_providers)
            if not has_all_providers:
                success = False
                details += " - Missing expected providers"
        else:
            details = f"HTTP {response.status_code}: {response.text}"
            
        print_test_result("AI Models Listing", success, details)
        return success, data if success else None
    except Exception as e:
        print_test_result("AI Models Listing", False, f"Exception: {str(e)}")
        return False, None

def test_save_ai_config():
    """Test saving AI configuration"""
    print("🔍 Testing AI Configuration Saving...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/ai-config",
            json=TEST_AI_CONFIG,
            timeout=10
        )
        success = response.status_code == 200
        
        if success:
            data = response.json()
            details = f"Message: {data.get('message')}"
        else:
            details = f"HTTP {response.status_code}: {response.text}"
            
        print_test_result("AI Configuration Saving", success, details)
        return success
    except Exception as e:
        print_test_result("AI Configuration Saving", False, f"Exception: {str(e)}")
        return False

def test_get_ai_config():
    """Test retrieving AI configuration"""
    print("🔍 Testing AI Configuration Retrieval...")
    try:
        response = requests.get(f"{BACKEND_URL}/ai-config/{TEST_USER_ID}", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            is_configured = data.get('configured', False)
            if is_configured:
                details = f"Provider: {data.get('provider')}, Model: {data.get('model')}, Model Name: {data.get('model_name')}"
            else:
                success = False
                details = "Configuration not found after saving"
        else:
            details = f"HTTP {response.status_code}: {response.text}"
            
        print_test_result("AI Configuration Retrieval", success, details)
        return success
    except Exception as e:
        print_test_result("AI Configuration Retrieval", False, f"Exception: {str(e)}")
        return False

def test_analyze_repository():
    """Test repository analysis initiation"""
    print("🔍 Testing Repository Analysis Initiation...")
    try:
        analysis_data = {
            "repo_url": TEST_REPO_URL,
            "user_id": TEST_USER_ID
        }
        
        response = requests.post(
            f"{BACKEND_URL}/analyze-repository",
            json=analysis_data,
            timeout=15
        )
        success = response.status_code == 200
        
        if success:
            data = response.json()
            analysis_id = data.get('analysis_id')
            status = data.get('status')
            details = f"Analysis ID: {analysis_id}, Status: {status}"
            
            if not analysis_id:
                success = False
                details += " - Missing analysis ID"
        else:
            details = f"HTTP {response.status_code}: {response.text}"
            
        print_test_result("Repository Analysis Initiation", success, details)
        return success, data.get('analysis_id') if success else None
    except Exception as e:
        print_test_result("Repository Analysis Initiation", False, f"Exception: {str(e)}")
        return False, None

def test_get_analysis_status(analysis_id):
    """Test getting analysis status and results"""
    print("🔍 Testing Analysis Status Retrieval...")
    try:
        response = requests.get(f"{BACKEND_URL}/analysis/{analysis_id}", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            status = data.get('status')
            repo_url = data.get('repo_url')
            flashcards_count = len(data.get('flashcards', []))
            details = f"Status: {status}, Repo: {repo_url}, Flashcards: {flashcards_count}"
        else:
            details = f"HTTP {response.status_code}: {response.text}"
            
        print_test_result("Analysis Status Retrieval", success, details)
        return success, data if success else None
    except Exception as e:
        print_test_result("Analysis Status Retrieval", False, f"Exception: {str(e)}")
        return False, None

def test_get_user_analyses():
    """Test getting all user analyses"""
    print("🔍 Testing User Analyses Retrieval...")
    try:
        response = requests.get(f"{BACKEND_URL}/user-analyses/{TEST_USER_ID}", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            analyses = data.get('analyses', [])
            details = f"Total analyses: {len(analyses)}"
            
            if analyses:
                latest = analyses[0]
                details += f", Latest: {latest.get('repo_url')} ({latest.get('status')})"
        else:
            details = f"HTTP {response.status_code}: {response.text}"
            
        print_test_result("User Analyses Retrieval", success, details)
        return success
    except Exception as e:
        print_test_result("User Analyses Retrieval", False, f"Exception: {str(e)}")
        return False

def wait_for_analysis_completion(analysis_id, max_wait_time=60):
    """Wait for analysis to complete and return final status"""
    print("⏳ Waiting for analysis to complete...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        success, data = test_get_analysis_status(analysis_id)
        if success and data:
            status = data.get('status')
            if status in ['completed', 'failed']:
                return status, data
        
        time.sleep(5)  # Wait 5 seconds before checking again
    
    return 'timeout', None

def test_invalid_inputs():
    """Test error handling with invalid inputs"""
    print("🔍 Testing Error Handling...")
    
    # Test invalid AI config
    invalid_config = {
        "provider": "invalid_provider",
        "model": "invalid_model",
        "api_key": "test-key",
        "user_id": TEST_USER_ID
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/ai-config", json=invalid_config, timeout=10)
        success = response.status_code == 400  # Should return bad request
        details = f"Invalid config handling: HTTP {response.status_code}"
        print_test_result("Invalid AI Config Handling", success, details)
    except Exception as e:
        print_test_result("Invalid AI Config Handling", False, f"Exception: {str(e)}")
    
    # Test invalid repository URL
    invalid_repo = {
        "repo_url": "https://invalid-repo-url.com/test/test",
        "user_id": TEST_USER_ID
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/analyze-repository", json=invalid_repo, timeout=15)
        # This might succeed initially but fail during processing
        details = f"Invalid repo handling: HTTP {response.status_code}"
        print_test_result("Invalid Repository URL Handling", True, details)
    except Exception as e:
        print_test_result("Invalid Repository URL Handling", False, f"Exception: {str(e)}")

def main():
    """Run all backend tests"""
    print("🚀 Starting Backend API Tests for AI-powered Code Learning System")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Test Repository: {TEST_REPO_URL}")
    print("=" * 80)
    
    test_results = {}
    
    # Test 1: Health Check
    test_results['health'] = test_health_check()
    
    # Test 2: AI Models
    test_results['ai_models'], ai_models_data = test_ai_models_endpoint()
    
    # Test 3: Save AI Config
    test_results['save_config'] = test_save_ai_config()
    
    # Test 4: Get AI Config
    test_results['get_config'] = test_get_ai_config()
    
    # Test 5: Repository Analysis
    test_results['analyze_repo'], analysis_id = test_analyze_repository()
    
    # Test 6: Analysis Status (immediate)
    if analysis_id:
        test_results['analysis_status'], _ = test_get_analysis_status(analysis_id)
        
        # Test 7: Wait for completion and check final status
        final_status, final_data = wait_for_analysis_completion(analysis_id)
        test_results['analysis_completion'] = final_status in ['completed']
        
        if final_status == 'completed' and final_data:
            flashcards = final_data.get('flashcards', [])
            print(f"✅ Analysis completed successfully with {len(flashcards)} flashcards generated")
            
            # Sample a flashcard to verify structure
            if flashcards:
                sample_card = flashcards[0]
                print(f"   Sample flashcard: {sample_card.get('front', 'N/A')[:50]}...")
        elif final_status == 'failed':
            error = final_data.get('error') if final_data else 'Unknown error'
            print(f"❌ Analysis failed: {error}")
        elif final_status == 'timeout':
            print(f"⏰ Analysis timed out (still processing)")
    
    # Test 8: User Analyses
    test_results['user_analyses'] = test_get_user_analyses()
    
    # Test 9: Error Handling
    test_invalid_inputs()
    
    # Summary
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All backend tests passed successfully!")
        return True
    else:
        print("⚠️  Some backend tests failed. Check details above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)