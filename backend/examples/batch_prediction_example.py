"""
Example usage of batch prediction API for student performance dashboard
Optimized for Render free tier deployment with Redis caching
"""

import requests
import json
import time
from typing import List, Dict

# API Configuration
API_BASE_URL = "https://your-app-name.onrender.com"  # Replace with your Render URL
API_KEY = "your-api-key"
JWT_TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def create_sample_students(count: int = 10) -> List[Dict]:
    """Create sample student data for testing"""
    import random
    
    students = []
    for i in range(count):
        student = {
            "comprehension": round(random.uniform(40, 95), 2),
            "attention": round(random.uniform(35, 90), 2),
            "focus": round(random.uniform(30, 95), 2),
            "retention": round(random.uniform(45, 90), 2),
            "engagement_time": random.randint(20, 180)
        }
        students.append(student)
    
    return students

def single_prediction_example():
    """Example of single student prediction"""
    print("=== Single Prediction Example ===")
    
    student_data = {
        "comprehension": 75.5,
        "attention": 82.0,
        "focus": 78.3,
        "retention": 80.1,
        "engagement_time": 120
    }
    
    response = requests.post(
        f"{API_BASE_URL}/predict",
        headers=headers,
        json=student_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Predicted Score: {result['predicted_score']:.2f}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def batch_prediction_example():
    """Example of batch student predictions with performance metrics"""
    print("\n=== Batch Prediction Example ===")
    
    # Create sample data
    students = create_sample_students(50)  # Test with 50 students
    
    batch_data = {
        "students": students
    }
    
    print(f"Sending batch request for {len(students)} students...")
    start_time = time.time()
    
    response = requests.post(
        f"{API_BASE_URL}/predict/batch",
        headers=headers,
        json=batch_data
    )
    
    request_time = (time.time() - start_time) * 1000
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"✅ Batch Processing Results:")
        print(f"   Total Students: {result['total_processed']}")
        print(f"   Cache Hits: {result['cache_hits']}")
        print(f"   Cache Hit Rate: {(result['cache_hits']/result['total_processed']*100):.1f}%")
        print(f"   Server Processing Time: {result['processing_time_ms']:.2f}ms")
        print(f"   Total Request Time: {request_time:.2f}ms")
        
        # Show first 5 predictions
        print(f"\n📊 Sample Predictions:")
        for i, pred in enumerate(result['predictions'][:5]):
            cached_indicator = "🟢" if pred['cached'] else "🔴"
            print(f"   Student {pred['student_index']}: {pred['predicted_score']:.2f} {cached_indicator}")
        
        if len(result['predictions']) > 5:
            print(f"   ... and {len(result['predictions']) - 5} more")
            
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

def cache_performance_test():
    """Test cache performance by running the same batch twice"""
    print("\n=== Cache Performance Test ===")
    
    # Create consistent test data
    students = create_sample_students(25)
    batch_data = {"students": students}
    
    # First request (should be cache misses)
    print("🔄 First request (cache misses expected)...")
    response1 = requests.post(f"{API_BASE_URL}/predict/batch", headers=headers, json=batch_data)
    
    if response1.status_code == 200:
        result1 = response1.json()
        print(f"   Cache Hits: {result1['cache_hits']}/{result1['total_processed']}")
        print(f"   Processing Time: {result1['processing_time_ms']:.2f}ms")
    
    # Second request (should be cache hits)
    print("🔄 Second request (cache hits expected)...")
    response2 = requests.post(f"{API_BASE_URL}/predict/batch", headers=headers, json=batch_data)
    
    if response2.status_code == 200:
        result2 = response2.json()
        print(f"   Cache Hits: {result2['cache_hits']}/{result2['total_processed']}")
        print(f"   Processing Time: {result2['processing_time_ms']:.2f}ms")
        
        # Calculate performance improvement
        if result1['processing_time_ms'] > 0:
            speedup = result1['processing_time_ms'] / result2['processing_time_ms']
            print(f"🚀 Cache Speedup: {speedup:.1f}x faster")

def get_cache_stats():
    """Get Redis cache statistics"""
    print("\n=== Cache Statistics ===")
    
    response = requests.get(f"{API_BASE_URL}/admin/cache/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print(f"📈 Redis Stats:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    else:
        print(f"❌ Error getting stats: {response.status_code}")

if __name__ == "__main__":
    print("🎓 Student Performance Dashboard - Batch Prediction Demo")
    print("=" * 60)
    
    try:
        # Run examples
        single_prediction_example()
        batch_prediction_example()
        cache_performance_test()
        get_cache_stats()
        
        print("\n✅ All examples completed successfully!")
        print("\n💡 Tips for Production:")
        print("   - Use batch predictions for better performance")
        print("   - Monitor cache hit rates for optimization")
        print("   - Stay within 100 students per batch for free tier")
        print("   - Cache expires after 1 hour to save Redis memory")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure your API is running and URL is correct")
    except Exception as e:
        print(f"❌ Error: {e}")
