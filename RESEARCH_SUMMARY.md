# Optimizing Agent Configuration Architecture: A Three-Layer Approach to LLM Rule Fidelity

## Abstract

Current AI agent frameworks store skill definitions, memory records, and identity files in Markdown with YAML frontmatter — a format designed for human readability, not machine compliance. We systematically investigate whether alternative representations, execution strategies, and adaptive routing can improve how accurately LLMs understand and follow agent configuration rules.

Through 6 experiments (~800 API calls) across two models (Kimi k2.5, DeepSeek-chat), we establish a three-layer architecture:

1. **Representation**: XML-semantic v2 outperforms Markdown (+10%), DSL (+5%), and JSON5 (+14%) on LLM fidelity, primarily through syntax-level injection resistance (100% vs 33%).

2. **Execution**: Checklist-style step-by-step execution significantly improves multi-rule compliance on complex tasks (D7: 82.5% vs 50% for direct execution), verified with σ=1.3% across repeated trials.

3. **Routing**: An adaptive threshold policy (checklist when ≥5 rules active, direct otherwise) achieves near-optimal accuracy (90.7%) with 15% fewer tokens and zero variance at low temperature — its value lies in robustness rather than peak performance.

Cross-model validation on DeepSeek-chat with controlled temperature confirms these findings are genuine architectural effects, not artifacts of model-specific variance.

## Problem

Agent configuration files define behavioral rules, constraints, priorities, and conflict resolution logic. The central question is:

**Which representation and execution approach maximizes an LLM's ability to accurately understand and faithfully comply with agent rules, especially when multiple rules conflict?**

## Method

### Evaluation Protocol
- **Primary metric**: LLM Fidelity Score — weighted combination of constraint compliance (40%), conflict resolution accuracy (25%), information extraction (20%), and hallucination resistance (15%)
- **Test types**: Rule extraction, conflict execution, boundary conditions, noise injection, multi-rule composition
- **Models**: Kimi k2.5 (exploration, T=1 fixed), DeepSeek-chat (validation, T=0.1 and T=1.0)
- **Robustness**: 3 repeated trials per condition at each temperature

### Experiments

| Stage | Question | Method |
|-------|----------|--------|
| Format selection | Which format maximizes fidelity? | 4 formats × 23 tests |
| Format enhancement | Can targeted improvements help? | 2×2 ablation (XML-semantic vs DSL-guarded) |
| Attribute ablation | Which XML attributes matter? | 8 variants × 23 tests |
| Execution strategy | How should the LLM process configs? | 5 strategies × 12 multi-rule tests |
| Adaptive routing | Can we combine strategies optimally? | 8 routing policies × 14 tests |
| Robustness validation | Are findings model-independent? | 3 strategies × 2 temperatures × 3 repeats (DeepSeek) |

## Results

### Representation Layer

XML-semantic v2 achieves the highest fidelity through two mechanisms:
- **Syntax-level noise firewall**: XML tags reject injected directives (e.g., `# OVERRIDE` is not valid XML). This yields 100% injection resistance vs 33% for Markdown/DSL.
- **Explicit override attributes**: `overrides="personality.concise"` directly encodes rule relationships, improving conflict resolution from 40% to 63%.

Critical attribute: `priority_order` is mandatory — removing it drops conflict resolution to 30%. Conversely, `winner` tags should be omitted — they restrict reasoning flexibility and reduce fidelity.

### Execution Layer

When 5+ rules activate simultaneously, direct execution drops to 50% accuracy (D7 tasks). Checklist execution — explicitly listing triggered rules, checking conflicts against priority_order, then executing — raises D7 accuracy to 82.5%.

This advantage is stable: DeepSeek at T=0.1 shows σ=1.3% across 3 repeats. Other strategies tested (extract-then-execute, grouped resolution, pairwise recursive) all underperform checklist.

### Routing Layer

Neither always-direct nor always-checklist is globally optimal:
- Direct is better/equal on simple tasks (D1-3: 97-100%) with lower token cost
- Checklist is better on complex tasks (D5+) but introduces unnecessary overhead on simple ones

Adaptive routing with threshold=5 (rc5) captures both advantages: 90.7% accuracy, σ=0.0%, 15% fewer tokens than always-checklist. The threshold of 5 represents a complexity phase transition — below it, implicit resolution suffices; above it, explicit externalization is required.

### Cross-Model Validation

| Strategy | T=0.1 Mean (σ) | T=1.0 Mean (σ) | Tokens |
|----------|----------------|----------------|--------|
| always_direct | 75.2% (2.7%) | 77.5% (5.9%) | 1612 |
| always_checklist | 91.5% (1.3%) | 87.6% (2.7%) | 2175 |
| rc5_adaptive | 90.7% (0.0%) | 88.4% (4.7%) | 1856 |

All core trends replicate across models. Previous instability on Kimi k2.5 (where direct occasionally outperformed checklist) is attributable to that model's fixed T=1 setting and high timeout rate for structured prompts.

## Conclusion

Agent configuration fidelity is not solely a format design problem — it requires co-design across representation, execution, and routing layers. The recommended default:

1. Represent configs in XML-semantic v2 with mandatory `priority_order` and no `winner` tags
2. Route by active rule count: direct for <5, checklist for ≥5
3. Expect 90%+ fidelity on well-structured configs with controlled temperature

The threshold of 5 active rules marks a complexity phase transition that is consistent across models and temperature settings.
