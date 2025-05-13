"""
Test script to examine how opacity values are grouped into buckets for visualization.
"""

from backend.backA.data_storage.value_manager import (
    create_opacity_buckets,
    get_bucket_for_value,
    get_bucket_opacity,
    calculate_opacity
)
from backend.backA.data_storage.database import get_node_value, set_node_value

def test_opacity_buckets():
    """Test how node values are grouped into opacity buckets."""
    # Create opacity buckets (default is 10)
    num_buckets = 5
    buckets = create_opacity_buckets(num_buckets)
    
    print(f"Created {num_buckets} opacity buckets:")
    for i, (min_val, max_val) in enumerate(buckets):
        opacity = get_bucket_opacity(i, buckets)
        print(f"Bucket {i}: {min_val:.2f}-{max_val:.2f} -> opacity {opacity:.2f}")
    
    print("\nTesting specific node values:")
    
    # Test values across the range
    test_values = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
    
    for value in test_values:
        # Calculate direct opacity (used for edges)
        direct_opacity = calculate_opacity(value)
        
        # Get bucket index and then bucket opacity (used for nodes)
        bucket_idx = get_bucket_for_value(value, buckets)
        bucket_opacity = get_bucket_opacity(bucket_idx, buckets)
        
        print(f"Value {value:.2f}: Direct opacity {direct_opacity:.2f}, Bucket {bucket_idx} opacity {bucket_opacity:.2f}")
    
    # Test a phenotype from our previous test
    test_hpo_id = "HP:0000252"  # Microcephaly
    
    # Read the current value
    current_value = get_node_value(test_hpo_id, 'phenotype')
    
    # Calculate direct opacity
    direct_opacity = calculate_opacity(current_value)
    
    # Get bucket index and then bucket opacity
    bucket_idx = get_bucket_for_value(current_value, buckets)
    bucket_opacity = get_bucket_opacity(bucket_idx, buckets)
    
    print(f"\nTest phenotype {test_hpo_id}:")
    print(f"Value: {current_value:.2f}, Direct opacity: {direct_opacity:.2f}")
    print(f"Bucket: {bucket_idx}, Bucket opacity: {bucket_opacity:.2f}")
    
    # Now simulate setting to different classifications
    print("\nSimulating different classifications:")
    
    # Present (1.0)
    value = 1.0
    bucket_idx = get_bucket_for_value(value, buckets)
    bucket_opacity = get_bucket_opacity(bucket_idx, buckets)
    print(f"Present (1.0): Bucket {bucket_idx}, Opacity {bucket_opacity:.2f}")
    
    # Uncertain (0.5)
    value = 0.5
    bucket_idx = get_bucket_for_value(value, buckets)
    bucket_opacity = get_bucket_opacity(bucket_idx, buckets)
    print(f"Uncertain (0.5): Bucket {bucket_idx}, Opacity {bucket_opacity:.2f}")
    
    # Absent (0.0)
    value = 0.0
    bucket_idx = get_bucket_for_value(value, buckets)
    bucket_opacity = get_bucket_opacity(bucket_idx, buckets)
    print(f"Absent (0.0): Bucket {bucket_idx}, Opacity {bucket_opacity:.2f}")

if __name__ == "__main__":
    test_opacity_buckets()