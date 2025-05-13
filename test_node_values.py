"""
Test script to examine node values in the database.
This script examines node values stored in the database and verifies that they're correctly set.
"""

from backend.backA.data_storage.database import get_node_value, set_node_value
from backend.backA.data_storage.value_manager import calculate_opacity, get_node_opacity

def test_node_values():
    """Test setting and retrieving node values."""
    # Get a sample HPO ID from the test
    test_hpo_id = "HP:0000252"  # Microcephaly
    
    print(f"Testing node values for {test_hpo_id}...")
    
    # Read the current value
    current_value = get_node_value(test_hpo_id, 'phenotype')
    current_opacity = calculate_opacity(current_value)
    
    print(f"Current value: {current_value:.2f}, opacity: {current_opacity:.2f}")
    
    # Set to 'Present' (1.0)
    set_node_value(test_hpo_id, 'phenotype', 1.0)
    print(f"Set value to 1.0 (Present)")
    
    # Read again
    new_value = get_node_value(test_hpo_id, 'phenotype')
    new_opacity = calculate_opacity(new_value)
    
    print(f"New value: {new_value:.2f}, opacity: {new_opacity:.2f}")
    
    # Set to 'Absent' (0.0)
    set_node_value(test_hpo_id, 'phenotype', 0.0)
    print(f"Set value to 0.0 (Absent)")
    
    # Read again
    new_value = get_node_value(test_hpo_id, 'phenotype')
    new_opacity = calculate_opacity(new_value)
    
    print(f"New value: {new_value:.2f}, opacity: {new_opacity:.2f}")
    
    # Set back to 'Uncertain' (0.5)
    set_node_value(test_hpo_id, 'phenotype', 0.5)
    print(f"Set value back to 0.5 (Uncertain)")
    
    # Read once more
    final_value = get_node_value(test_hpo_id, 'phenotype')
    final_opacity = calculate_opacity(final_value)
    
    print(f"Final value: {final_value:.2f}, opacity: {final_opacity:.2f}")

if __name__ == "__main__":
    test_node_values()