"""
Quick script to set a specific node value and see the effect.
"""

import sys
from backend.backA.data_storage.value_manager import set_node_value
from backend.backA.data_storage.database import get_node_value

if len(sys.argv) < 3:
    print("Usage: python test_update_node.py <hpo_id> <value>")
    sys.exit(1)

hpo_id = sys.argv[1]
value = float(sys.argv[2])

# Get current value
current = get_node_value(hpo_id, 'phenotype')
print(f"Current value for {hpo_id}: {current}")

# Set new value
set_node_value(hpo_id, 'phenotype', value)
print(f"Set value to {value}")

# Get updated value
updated = get_node_value(hpo_id, 'phenotype')
print(f"Updated value for {hpo_id}: {updated}")

print("You can now go to the Knowledge Graph tab and refresh the page to see if the changes take effect.")