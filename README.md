# Agent Config Architecture: Representation, Execution, and Routing

**How should AI agents read and follow their configuration files?**

This project systematically investigates how file format, execution strategy, and adaptive routing affect an LLM's ability to accurately understand and comply with agent configuration rules — through 6 experiments, ~800 API calls, and cross-model validation.

---

## Key Findings

### Three-Layer Architecture

| Layer | Finding | Evidence |
|-------|---------|----------|
| **Representation** | XML-semantic v2 is the optimal config format | Outperforms Markdown (+10%), DSL (+5%), JSON5 (+14%) on LLM fidelity. XML tags provide syntax-level noise firewalls (100% injection resistance). |
| **Execution** | Checklist-style execution significantly outperforms direct execution on complex tasks | D7 accuracy: checklist 82.5% vs direct 50% (DeepSeek, T=0.1, σ=1.3%) |
| **Routing** | Adaptive threshold routing (rc5) is the robust default | Near-checklist accuracy (90.7%) with 15% fewer tokens and σ=0.0% at low temperature |

### The Default Architecture

```
┌─────────────────────────────────────────────┐
│  XML-semantic v2 Config                     │
│  ┌───────────────────────────────────────┐  │
│  │ <priority_order>                      │  │
│  │   safety > honesty > help > persona   │  │
│  │ </priority_order>                     │  │
│  │                                       │  │
│  │ <rules>                               │  │
│  │   <rule id="R7"                       │  │
│  │     overrides="personality.concise">  │  │
│  │     Teaching mode for beginners       │  │
│  │   </rule>                             │  │
│  │ </rules>                              │  │
│  │                                       │  │
│  │ <conflicts>                           │  │
│  │   Natural language resolution         │  │
│  │   (no winner tags)                    │  │
│  │ </conflicts>                          │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│  Adaptive Router (rc5)                      │
│                                             │
│  active_rules < 5  ──→  Direct Execution    │
│  active_rules ≥ 5  ──→  Checklist Execution │
│                                             │
│  Checklist:                                 │
│  □ List triggered rules                     │
│  □ List triggered constraints               │
│  □ Check conflicts → priority_order         │
│  □ Check exceptions                         │
│  □ Final action list                        │
│  □ Execute                                  │
└─────────────────────────────────────────────┘
```

---

## Experiment Summary

| # | Experiment | Model | Key Result |
|---|-----------|-------|------------|
| 01 | Format Comparison (4 formats × 23 tests) | Kimi k2.5 | XML 62.0 > DSL 61.8 > MD 56.7 > JSON5 56.2 |
| 02 | Format Enhancement (2×2 matrix) | Kimi k2.5 | XML-semantic 64.5 >> DSL-guarded 57.7 |
| 03 | Ablation + Compression + Stress | Kimi k2.5 | `priority_order` essential; `winner` tags harmful; 100% injection resistance |
| 04 | Execution Strategy (5 strategies) | Kimi k2.5 | checklist 66.7% > direct 60.8% > pairwise 43.1% |
| 05 | Adaptive Routing (8 policies) | Kimi k2.5 | rc5 66.0% > always_checklist 60.0% > always_direct 48.0% |
| **06** | **Robustness (3×2×3 repeats)** | **DeepSeek** | **rc5 90.7% (σ=0.0%) — cross-model validated** |

---

## Why These Choices?

### Why XML over Markdown/DSL/JSON?

| Format | Fidelity | Weakness |
|--------|----------|----------|
| **XML** | 62.0 | Slightly more tokens (+31%) |
| Markdown | 56.7 | No syntax boundary — any injected text looks valid |
| DSL | 61.8 | `# OVERRIDE` looks like a real directive — no syntax firewall |
| JSON5 | 56.2 | Worst conflict resolution (30%) — flat key-value can't express priority |

XML tags create **syntax-level noise firewalls**: `# OVERRIDE` is not valid XML, so the LLM rejects it. This gave XML 100% injection resistance vs 33% for Markdown and DSL.

### Why `priority_order` is mandatory

Ablation experiment: removing `priority_order` crashed conflict resolution from 43% to **30%** — the single largest drop across all attribute removals. It's the LLM's only anchor for resolving rule conflicts.

### Why `winner` tags are harmful

Removing `winner` attributes *increased* fidelity. Overly explicit resolution tags appear to restrict the LLM's reasoning flexibility in unforeseen conflict scenarios. Natural language conflict descriptions work better.

### Why checklist beats direct on complex tasks

| Difficulty | Direct | Checklist | Gap |
|-----------|--------|-----------|-----|
| D1-3 | 97% | 100% | +3 |
| D5 | 91% | **100%** | **+9** |
| D7 | 50% | **82.5%** | **+32.5** |

At 5+ simultaneously active rules, the LLM needs explicit step-by-step externalization to avoid dropping constraints. Below 5 rules, direct execution is sufficient and cheaper.

### Why the threshold is 5

Tested thresholds at 3, 4, and 5. At rc5: simple tasks stay on direct (faster, equally accurate), and only complex tasks pay the checklist token cost. The threshold captures a **complexity phase transition** — 4 rules are manageable implicitly, 5+ require explicit resolution.

---

## Cross-Model Validation

DeepSeek-chat with controlled temperature (0.1 and 1.0), 3 repeats per test:

| Strategy | T=0.1 Mean | T=0.1 σ | T=1.0 Mean | T=1.0 σ | Null% | Tokens |
|----------|-----------|---------|-----------|---------|-------|--------|
| always_direct | 75.2% | 2.7% | 77.5% | 5.9% | 0% | 1612 |
| always_checklist | **91.5%** | 1.3% | 87.6% | 2.7% | 0% | 2175 |
| **rc5_adaptive** | 90.7% | **0.0%** | **88.4%** | 4.7% | 0% | **1856** |

- **Zero null responses** on DeepSeek (vs up to 45% null on Kimi k2.5 for structured strategies)
- Checklist advantage on D5+ is **real and stable**, not a Kimi variance artifact
- rc5 achieves the **lowest variance** (σ=0.0% at T=0.1) — its value is robustness, not peak accuracy

---

## Repository Structure

```
├── FINAL_ARCHITECTURE.md           # Complete design decision record
├── README.md                       # This file
├── baselines/                      # Baseline test materials (skill + identity configs)
├── experiments/
│   ├── 01_file_format/             # Format comparison + ablation + compression + stress
│   ├── 04_multirule/               # 5 execution strategies comparison
│   ├── 05_adaptive/                # Adaptive routing + validation
│   └── 06_robustness/              # Cross-model robustness study (DeepSeek)
└── results/                        # All raw data + reports (JSON + Markdown)
```

---

## Reproduce

Requirements: Python 3, API keys for Kimi (Moonshot) and/or DeepSeek.

```bash
# Run format comparison (Experiment 01)
cd experiments/01_file_format && python3 run_test.py

# Run execution strategy comparison (Experiment 04)
cd experiments/04_multirule && python3 run_experiment.py

# Run robustness study with DeepSeek (Experiment 06)
cd experiments/06_robustness && python3 run_experiment.py
```

---

## Limitations

- Tested on Kimi k2.5 and DeepSeek-chat only. Generalization to other LLMs (GPT-4, Claude, Llama) not yet validated.
- Test set covers code-review skill and engineering-advisor identity. Other agent types may behave differently.
- `active_rules` count is currently manual. Automated rule-activation detection is future work.
- Kimi k2.5 is locked at temperature=1, which inflated variance in Experiments 01-05.

---

## What's Next

- **Migration validation**: Test the three-layer architecture on different agent types (customer service, data analysis)
- **Router prototype**: Build `adaptive_rc5` as a callable routing module
- **Automated rule counting**: Detect `active_rules` from config + user query automatically
- **Tokenizer research**: Investigate alternatives to subword tokenization for agent instruction processing (Direction 2 from original project scope)
