#!/usr/bin/env python3
"""
Test script for clustering batch endpoint
"""

import requests
import json

def test_clustering_endpoint():
    """Test the clustering batch endpoint"""
    
    # Test data
    test_data = {
        "students": [
            {
                "comprehension": 75.5,
                "attention": 82.0,
                "focus": 78.3,
                "retention": 80.1,
                "engagement_time": 120
            },
            {
                "comprehension": 65.0,
                "attention": 70.0,
                "focus": 68.5,
                "retention": 72.0,
                "engagement_time": 90
            }
        ]
    }
    
    # Test locally first
    url = "http://localhost:8000/cluster/batch"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "demo_key",
        "Authorization": "Bearer demo_token"
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Clustering endpoint test passed!")
        else:
            print("❌ Clustering endpoint test failed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_clustering_endpoint()
