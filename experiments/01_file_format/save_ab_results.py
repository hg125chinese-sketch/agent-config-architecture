#!/usr/bin/env python3
"""从日志中提取 Part A/B 已有结果并保存"""
import json
import os
import re

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "results")
LOG_FILE = "/tmp/claude-1000/-home-nixos-agent-breakthrough/d3eb2e30-670d-446b-875a-f84808988992/tasks/bpub0ud6m.output"

# Parse log to extract results
with open(LOG_FILE) as f:
    log = f.read()

# Extract Part A results
ablation_data = {}
pattern = r'---\s*变体:\s*(\S+)\s*---.*?\n\s+\1:\s+Fidelity=(\S+)\s+抽取=(\d+)%\s+冲突=(\d+)%\s+边界=(\d+)%\s+干扰=(\d+)%\s+tokens=(\d+)'
for m in re.finditer(pattern, log):
    name = m.group(1)
    ablation_data[name] = {
        "fidelity": float(m.group(2)),
        "task_scores": {
            "task1": {"pct": int(m.group(3))},
            "task2": {"pct": int(m.group(4))},
            "task3": {"pct": int(m.group(5))},
            "task4": {"pct": int(m.group(6))},
        },
        "tokens_total": int(m.group(7)),
    }

# Extract Part B results
compression_data = {}
pattern_b = r'(\w+):\s+Fidelity=(\S+)\s+tokens=(\d+)\s+fidelity/1k_tokens=(\S+)'
for m in re.finditer(pattern_b, log):
    name = m.group(1)
    compression_data[name] = {
        "fidelity": float(m.group(2)),
        "tokens_total": int(m.group(3)),
        "fidelity_per_1k": float(m.group(4)),
    }

all_results = {
    "part_a_ablation": ablation_data,
    "part_b_compression": compression_data,
}

output_path = os.path.join(RESULTS_DIR, "03_v2_study_results.json")
os.makedirs(RESULTS_DIR, exist_ok=True)
with open(output_path, "w") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"Saved Part A ({len(ablation_data)} variants) and Part B ({len(compression_data)} variants)")
print(f"Part A: {json.dumps({k: v['fidelity'] for k,v in ablation_data.items()}, indent=2)}")
print(f"Part B: {json.dumps({k: v['fidelity'] for k,v in compression_data.items()}, indent=2)}")
