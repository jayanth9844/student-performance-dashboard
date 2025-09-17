#!/usr/bin/env python3
"""
Test script to verify batch prediction endpoints are working correctly
"""
import requests
import json
import time

# API Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your-secret-api-key"  # Default from docker-compose
USERNAME = "testuser"
PASSWORD = "testpass"

def get_auth_token():
    """Get JWT token for authentication"""
    auth_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/token", data=auth_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Authentication failed: {response.status_code}")
        print(response.text)
        return None

def test_batch_score_prediction(token):
    """Test batch score prediction endpoint"""
    print("\n=== Testing Batch Score Prediction ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Test data with 3 students
    test_data = {
        "students": [
            {
                "comprehension": 85.0,
                "attention": 78.0,
                "focus": 82.0,
                "retention": 88.0,
                "engagement_time": 45
            },
            {
                "comprehension": 92.0,
                "attention": 89.0,
                "focus": 91.0,
                "retention": 94.0,
                "engagement_time": 55
            },
            {
                "comprehension": 76.0,
                "attention": 72.0,
                "focus": 74.0,
                "retention": 79.0,
                "engagement_time": 38
            }
        ]
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/predict/batch", headers=headers, json=test_data)
    end_time = time.time()
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {(end_time - start_time)*1000:.2f}ms")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total Processed: {result['total_processed']}")
        print(f"Cache Hits: {result['cache_hits']}")
        print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
        print("Predictions:")
        for pred in result['predictions']:
            print(f"  Student {pred['student_index']}: Score {pred['predicted_score']:.2f} (Cached: {pred['cached']})")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_batch_clustering_prediction(token):
    """Test batch clustering prediction endpoint"""
    print("\n=== Testing Batch Clustering Prediction ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Test data with 3 students
    test_data = {
        "students": [
            {
                "comprehension": 85.0,
                "attention": 78.0,
                "focus": 82.0,
                "retention": 88.0,
                "engagement_time": 45
            },
            {
                "comprehension": 92.0,
                "attention": 89.0,
                "focus": 91.0,
                "retention": 94.0,
                "engagement_time": 55
            },
            {
                "comprehension": 76.0,
                "attention": 72.0,
                "focus": 74.0,
                "retention": 79.0,
                "engagement_time": 38
            }
        ]
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/cluster/batch", headers=headers, json=test_data)
    end_time = time.time()
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {(end_time - start_time)*1000:.2f}ms")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total Processed: {result['total_processed']}")
        print(f"Cache Hits: {result['cache_hits']}")
        print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
        print(f"Available Personas: {result['available_personas']}")
        print("Predictions:")
        for pred in result['predictions']:
            print(f"  Student {pred['student_index']}: Cluster {pred['cluster_label']} - {pred['persona_name']} ({pred['confidence']}) (Cached: {pred['cached']})")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_personas_endpoint(token):
    """Test personas endpoint"""
    print("\n=== Testing Personas Endpoint ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-API-Key": API_KEY
    }
    
    response = requests.get(f"{BASE_URL}/personas", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total Clusters: {result['total_clusters']}")
        print(f"Available Personas: {result['personas']}")
        print(f"Cluster Mapping: {result['cluster_mapping']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def main():
    """Main test function"""
    print("Starting API Tests...")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token. Exiting.")
        return
    
    print(f"Authentication successful!")
    
    # Test all endpoints
    tests = [
        test_batch_score_prediction,
        test_batch_clustering_prediction,
        test_personas_endpoint
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func(token)
            results.append(result)
        except Exception as e:
            print(f"Test {test_func.__name__} failed with error: {e}")
            results.append(False)
    
    # Summary
    print("\n=== Test Summary ===")
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Batch prediction endpoints are working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
