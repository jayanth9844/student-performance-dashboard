"""
Example usage of clustering prediction API for student performance dashboard
Demonstrates single and batch clustering predictions with persona identification
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
    """Create sample student data for clustering testing"""
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

def single_clustering_example():
    """Example of single student clustering prediction"""
    print("=== Single Student Clustering Example ===")
    
    student_data = {
        "comprehension": 85.5,
        "attention": 88.0,
        "focus": 82.3,
        "retention": 86.1,
        "engagement_time": 150
    }
    
    response = requests.post(
        f"{API_BASE_URL}/cluster",
        headers=headers,
        json=student_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Student Profile:")
        print(f"  Cluster: {result['cluster_label']}")
        print(f"  Persona: {result['persona_name']}")
        print(f"  Confidence: {result['confidence']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def batch_clustering_example():
    """Example of batch student clustering predictions"""
    print("\n=== Batch Student Clustering Example ===")
    
    # Create sample data with different performance profiles
    students = [
        # High performer
        {"comprehension": 85, "attention": 88, "focus": 82, "retention": 86, "engagement_time": 150},
        # Low engagement risk
        {"comprehension": 45, "attention": 42, "focus": 38, "retention": 44, "engagement_time": 30},
        # Consistent learner
        {"comprehension": 72, "attention": 75, "focus": 70, "retention": 73, "engagement_time": 90},
        # Developing performer
        {"comprehension": 65, "attention": 58, "focus": 62, "retention": 68, "engagement_time": 75},
    ]
    
    batch_data = {
        "students": students
    }
    
    print(f"Sending batch clustering request for {len(students)} students...")
    start_time = time.time()
    
    response = requests.post(
        f"{API_BASE_URL}/cluster/batch",
        headers=headers,
        json=batch_data
    )
    
    request_time = (time.time() - start_time) * 1000
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"✅ Batch Clustering Results:")
        print(f"   Total Students: {result['total_processed']}")
        print(f"   Cache Hits: {result['cache_hits']}")
        print(f"   Cache Hit Rate: {(result['cache_hits']/result['total_processed']*100):.1f}%")
        print(f"   Server Processing Time: {result['processing_time_ms']:.2f}ms")
        print(f"   Total Request Time: {request_time:.2f}ms")
        
        print(f"\n🎭 Student Personas:")
        for pred in result['predictions']:
            cached_indicator = "🟢" if pred['cached'] else "🔴"
            print(f"   Student {pred['student_index']}: {pred['persona_name']} (Cluster {pred['cluster_label']}) {cached_indicator}")
        
        print(f"\n📊 Available Personas:")
        for persona in result['available_personas']:
            print(f"   • {persona}")
            
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

def get_available_personas():
    """Get list of available student personas"""
    print("\n=== Available Student Personas ===")
    
    response = requests.get(f"{API_BASE_URL}/personas", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"📚 Total Clusters: {result['total_clusters']}")
        print(f"🎭 Available Personas:")
        for cluster_id, persona_name in result['cluster_mapping'].items():
            print(f"   Cluster {cluster_id}: {persona_name}")
    else:
        print(f"❌ Error getting personas: {response.status_code}")

def clustering_performance_test():
    """Test clustering performance with larger batch"""
    print("\n=== Clustering Performance Test ===")
    
    # Create larger sample for performance testing
    students = create_sample_students(50)
    batch_data = {"students": students}
    
    print(f"🔄 Testing clustering performance with {len(students)} students...")
    
    # First request (should be cache misses)
    start_time = time.time()
    response1 = requests.post(f"{API_BASE_URL}/cluster/batch", headers=headers, json=batch_data)
    first_request_time = (time.time() - start_time) * 1000
    
    if response1.status_code == 200:
        result1 = response1.json()
        print(f"   First Request:")
        print(f"     Cache Hits: {result1['cache_hits']}/{result1['total_processed']}")
        print(f"     Processing Time: {result1['processing_time_ms']:.2f}ms")
        print(f"     Total Request Time: {first_request_time:.2f}ms")
        
        # Count personas
        persona_counts = {}
        for pred in result1['predictions']:
            persona = pred['persona_name']
            persona_counts[persona] = persona_counts.get(persona, 0) + 1
        
        print(f"   📊 Persona Distribution:")
        for persona, count in persona_counts.items():
            percentage = (count / len(students)) * 100
            print(f"     {persona}: {count} students ({percentage:.1f}%)")
    
    # Second request (should have more cache hits)
    print(f"🔄 Second request (testing cache effectiveness)...")
    start_time = time.time()
    response2 = requests.post(f"{API_BASE_URL}/cluster/batch", headers=headers, json=batch_data)
    second_request_time = (time.time() - start_time) * 1000
    
    if response2.status_code == 200:
        result2 = response2.json()
        print(f"   Second Request:")
        print(f"     Cache Hits: {result2['cache_hits']}/{result2['total_processed']}")
        print(f"     Processing Time: {result2['processing_time_ms']:.2f}ms")
        print(f"     Total Request Time: {second_request_time:.2f}ms")
        
        if result1['processing_time_ms'] > 0:
            speedup = result1['processing_time_ms'] / result2['processing_time_ms']
            print(f"🚀 Cache Speedup: {speedup:.1f}x faster")

if __name__ == "__main__":
    print("🎭 Student Performance Dashboard - Clustering Demo")
    print("=" * 60)
    
    try:
        # Run examples
        get_available_personas()
        single_clustering_example()
        batch_clustering_example()
        clustering_performance_test()
        
        print("\n✅ All clustering examples completed successfully!")
        print("\n💡 Clustering Insights:")
        print("   - Students are grouped into 4 distinct learning personas")
        print("   - Clustering helps identify learning patterns and needs")
        print("   - Batch processing optimized for Redis free tier")
        print("   - Cache expires after 5 minutes to save memory")
        print("   - Use clustering to personalize learning experiences")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure your API is running and URL is correct")
    except Exception as e:
        print(f"❌ Error: {e}")
