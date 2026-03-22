#!/usr/bin/env python3
"""只跑 Part C 压力测试，然后合并到完整报告"""

import json
import os
import sys

# 复用 v2 study 的所有定义
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_v2_study import (
    run_stress_tests, load_baseline_xml, COMPRESSION_VARIANTS,
    RESULTS_DIR, estimate_tokens
)

def main():
    skill_baseline = load_baseline_xml("skill")
    identity_baseline = load_baseline_xml("identity")

    stress_results = {}

    print("=" * 70)
    print("  PART C: 外部有效性压力测试")
    print("=" * 70)

    # full_verbose
    print(f"\n--- 压力测试: full_verbose ---")
    stress_results["full_verbose"] = run_stress_tests(
        skill_baseline, identity_baseline, label="[full]")
    print(f"  full_verbose: {stress_results['full_verbose']['pct']}%")

    # compact_attr (best compact from Part B)
    print(f"\n--- 压力测试: compact_attr ---")
    transform_fn = COMPRESSION_VARIANTS["compact_attr"]
    stress_results["compact_attr"] = run_stress_tests(
        transform_fn(skill_baseline), transform_fn(identity_baseline),
        label="[compact]")
    print(f"  compact_attr: {stress_results['compact_attr']['pct']}%")

    # ultra_compact
    print(f"\n--- 压力测试: ultra_compact ---")
    transform_fn = COMPRESSION_VARIANTS["ultra_compact"]
    stress_results["ultra_compact"] = run_stress_tests(
        transform_fn(skill_baseline), transform_fn(identity_baseline),
        label="[ultra]")
    print(f"  ultra_compact: {stress_results['ultra_compact']['pct']}%")

    # 加载已有结果并合并
    results_path = os.path.join(RESULTS_DIR, "03_v2_study_results.json")
    if os.path.exists(results_path):
        with open(results_path) as f:
            all_results = json.load(f)
    else:
        all_results = {}

    all_results["part_c_stress"] = stress_results

    with open(results_path, "w") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # 打印汇总
    print("\n" + "=" * 70)
    print("  Part C 汇总")
    print("=" * 70)
    for name, data in stress_results.items():
        print(f"\n  {name}: {data['pct']}% ({data['total_earned']}/{data['total_max']})")
        by_type = {}
        for r in data["results"]:
            t = r["type"]
            if t not in by_type:
                by_type[t] = {"earned": 0, "max": 0}
            by_type[t]["earned"] += r["score"]
            by_type[t]["max"] += r["max"]
        for t, d in by_type.items():
            pct = d["earned"] / d["max"] * 100 if d["max"] > 0 else 0
            print(f"    {t:25s}: {pct:.0f}%")

    print("\n完成！已合并到", results_path)


if __name__ == "__main__":
    main()
