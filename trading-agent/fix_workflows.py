#!/usr/bin/env python3
import json
import os
from pathlib import Path

workflows_dir = Path(__file__).parent / "workflows"

for wf_path in workflows_dir.glob("*.json"):
    with open(wf_path, 'r') as f:
        d = json.load(f)

    changed = False
    for node in d.get('nodes', []):
        if node.get('type') == 'n8n-nodes-base.httpRequest':
            # Remove authentication parameter
            if 'authentication' in node.get('parameters', {}):
                del node['parameters']['authentication']
                changed = True

            # Ensure credentials is a dict (even if empty)
            if 'credentials' not in node:
                node['credentials'] = {}
                changed = True

            print(f"Fixed: {wf_path.name} - {node.get('name')}")

    if changed:
        with open(wf_path, 'w') as f:
            json.dump(d, f, indent=2)

print("Done!")
