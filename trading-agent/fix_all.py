#!/usr/bin/env python3
import json
from pathlib import Path

workflows_dir = Path(__file__).parent / "workflows"

for wf_path in workflows_dir.glob("*.json"):
    with open(wf_path, 'r') as f:
        d = json.load(f)

    fixed = False
    for node in d.get('nodes', []):
        if node.get('type') == 'n8n-nodes-base.httpRequest':
            if 'credentials' not in node:
                node['credentials'] = {}
                fixed = True
                print(f"Fixed {wf_path.name}: {node.get('name')} - added credentials {{}}")

    if fixed:
        with open(wf_path, 'w') as f:
            json.dump(d, f, indent=2)

print("Done!")
