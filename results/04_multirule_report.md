# Experiment 04: Multi-rule Composition Failure Study

## 1. 执行摘要

测试了 5 种执行策略 × 11 道多规则组合题。

| # | 策略 | 总准确率 | 约束违反 | 平均 tokens | 平均回应长度 |
|---|------|----------|----------|-------------|-------------|
| 1 | checklist | 66.7% | 17 | 3779 | 1476 |
| 2 | direct | 60.8% | 20 | 3142 | 1050 |
| 3 | extract_then_execute | 52.9% | 24 | 3760 | 820 |
| 4 | grouped | 52.9% | 24 | 3815 | 1207 |
| 5 | pairwise | 43.1% | 29 | 3847 | 758 |

## 2. 各难度层级表现

| 策略 | 难度3 | 难度4 | 难度5 | 难度6 | 难度7 |
|------|-------|-------|-------|-------|-------|
| checklist | 50.0% | 0.0% | 80.0% | 100.0% | 78.9% |
| direct | 83.3% | 28.6% | 73.3% | 50.0% | 57.9% |
| extract_then_execute | 50.0% | 28.6% | 53.3% | 100.0% | 52.6% |
| grouped | 50.0% | 28.6% | 60.0% | 100.0% | 47.4% |
| pairwise | 50.0% | 28.6% | 33.3% | 75.0% | 47.4% |

## 3. 各冲突类型表现

| 策略 | chain_override | cross_block | exception_override | priority_chain | synonym_conflict |
|------|-------|-------|-------|-------|-------|
| checklist | 81.8% | 0.0% | 0.0% | 83.3% | 0.0% |
| direct | 63.6% | 100.0% | 25.0% | 63.3% | 33.3% |
| extract_then_execute | 81.8% | 0.0% | 0.0% | 53.3% | 66.7% |
| grouped | 81.8% | 0.0% | 0.0% | 53.3% | 66.7% |
| pairwise | 72.7% | 0.0% | 0.0% | 40.0% | 66.7% |

## 4. 噪声影响

| 策略 | 无噪声 | 有噪声 | Δ |
|------|--------|--------|---|
| checklist | 65.9% | 70.0% | +4.1 |
| direct | 65.9% | 40.0% | -25.9 |
| extract_then_execute | 53.7% | 50.0% | -3.7 |
| grouped | 56.1% | 40.0% | -16.1 |
| pairwise | 43.9% | 40.0% | -3.9 |

## 5. 逐题详细结果

### checklist (66.7%)

- ✓ **M3_1** 3-rule: beginner + production + code: 3/3
- ✗ **M3_2** 3-rule: security + generated + empty desc: 0/3 — 未命中: HC4 安全团队, HC5 跳过 generated, HC6 请求描述
- ✓ **M5_1** 5-rule: full PR scenario: 5/5
- ✓ **M5_2** 5-rule: beginner + production + code + disagree + failure: 5/5
- △ **M7_1** 7-rule: maximum complexity PR: 5/7 — 未命中: Changes Requested (有 CRITICAL), 评论数 ≤ 15
- △ **M7_2** 7-rule: identity mega-conflict: 5/7 — 未命中: R5 vs R3 冲突 → R3 赢, R4 不额外扩展范围
- ✗ **SYN_1** synonym: concise vs teaching vs failure-mode: 0/3 — 未命中: R7 覆盖 concise, R1 两者都说 failure mode, 不能只说简短答案
- ✗ **EXC_1** exception: style skip + few lines + generated: 0/4 — 未命中: file 1: HC5 generated 跳过, file 2: style 正常检查（≥10行）, file 2 warning, verdict 综合
- ✓ **CHAIN_1** chain: R7→concise, R5→R3, R6→production, R1→failure: 4/4
- △ **M5_N** 5-rule + light noise: 2/5 — 未命中: HC4 安全团队, HC6 请求描述, 不跳过（非 generated）
- ✓ **M7_N** 7-rule + light noise: 5/5

### direct (60.8%)

- △ **M3_1** 3-rule: beginner + production + code: 2/3 — 未命中: R1 failure mode
- ✓ **M3_2** 3-rule: security + generated + empty desc: 3/3
- ✓ **M5_1** 5-rule: full PR scenario: 5/5
- △ **M5_2** 5-rule: beginner + production + code + disagree + failure: 2/5 — 未命中: R7 教学模式, R3 代码可能超 30 行, C3 反对一次
- △ **M7_1** 7-rule: maximum complexity PR: 6/7 — 未命中: 按 priority 排序评论
- △ **M7_2** 7-rule: identity mega-conflict: 5/7 — 未命中: R5 vs R3 冲突 → R3 赢, R4 不额外扩展范围
- △ **SYN_1** synonym: concise vs teaching vs failure-mode: 1/3 — 未命中: R7 覆盖 concise, 不能只说简短答案
- △ **EXC_1** exception: style skip + few lines + generated: 1/4 — 未命中: file 2: style 正常检查（≥10行）, file 2 warning, verdict 综合
- △ **CHAIN_1** chain: R7→concise, R5→R3, R6→production, R1→failure: 2/4 — 未命中: R5 要给代码但 R3 限制 → 先问, R1 failure mode
- △ **M5_N** 5-rule + light noise: 4/5 — 未命中: 不跳过（非 generated）
- ✗ **M7_N** 7-rule + light noise: 0/5 — 未命中: R7 教学模式, R6 production, R1 failure mode, R3 先问, R5 代码示例

### extract_then_execute (52.9%)

- ✓ **M3_1** 3-rule: beginner + production + code: 3/3
- ✗ **M3_2** 3-rule: security + generated + empty desc: 0/3 — 未命中: HC4 安全团队, HC5 跳过 generated, HC6 请求描述
- △ **M5_1** 5-rule: full PR scenario: 4/5 — 未命中: HC6 请求描述
- △ **M5_2** 5-rule: beginner + production + code + disagree + failure: 4/5 — 未命中: R3 代码可能超 30 行
- ✗ **M7_1** 7-rule: maximum complexity PR: 0/7 — 未命中: HC4 安全团队, HC3 文件大小 >500, HC6 请求描述, Changes Requested (有 CRITICAL), 评论数 ≤ 15, 按 priority 排序评论, 第 3 次未超限，可执行
- △ **M7_2** 7-rule: identity mega-conflict: 5/7 — 未命中: R5 vs R3 冲突 → R3 赢, R4 不额外扩展范围
- △ **SYN_1** synonym: concise vs teaching vs failure-mode: 2/3 — 未命中: 不能只说简短答案
- ✗ **EXC_1** exception: style skip + few lines + generated: 0/4 — 未命中: file 1: HC5 generated 跳过, file 2: style 正常检查（≥10行）, file 2 warning, verdict 综合
- ✓ **CHAIN_1** chain: R7→concise, R5→R3, R6→production, R1→failure: 4/4
- ✗ **M5_N** 5-rule + light noise: 0/5 — 未命中: HC4 安全团队, HC3 文件大小 >500, HC6 请求描述, Changes Requested, 不跳过（非 generated）
- ✓ **M7_N** 7-rule + light noise: 5/5

### grouped (52.9%)

- ✓ **M3_1** 3-rule: beginner + production + code: 3/3
- ✗ **M3_2** 3-rule: security + generated + empty desc: 0/3 — 未命中: HC4 安全团队, HC5 跳过 generated, HC6 请求描述
- ✓ **M5_1** 5-rule: full PR scenario: 5/5
- △ **M5_2** 5-rule: beginner + production + code + disagree + failure: 4/5 — 未命中: R3 代码可能超 30 行
- ✗ **M7_1** 7-rule: maximum complexity PR: 0/7 — 未命中: HC4 安全团队, HC3 文件大小 >500, HC6 请求描述, Changes Requested (有 CRITICAL), 评论数 ≤ 15, 按 priority 排序评论, 第 3 次未超限，可执行
- △ **M7_2** 7-rule: identity mega-conflict: 5/7 — 未命中: R5 vs R3 冲突 → R3 赢, R4 不额外扩展范围
- △ **SYN_1** synonym: concise vs teaching vs failure-mode: 2/3 — 未命中: 不能只说简短答案
- ✗ **EXC_1** exception: style skip + few lines + generated: 0/4 — 未命中: file 1: HC5 generated 跳过, file 2: style 正常检查（≥10行）, file 2 warning, verdict 综合
- ✓ **CHAIN_1** chain: R7→concise, R5→R3, R6→production, R1→failure: 4/4
- ✗ **M5_N** 5-rule + light noise: 0/5 — 未命中: HC4 安全团队, HC3 文件大小 >500, HC6 请求描述, Changes Requested, 不跳过（非 generated）
- △ **M7_N** 7-rule + light noise: 4/5 — 未命中: R3 先问

### pairwise (43.1%)

- ✓ **M3_1** 3-rule: beginner + production + code: 3/3
- ✗ **M3_2** 3-rule: security + generated + empty desc: 0/3 — 未命中: HC4 安全团队, HC5 跳过 generated, HC6 请求描述
- ✗ **M5_1** 5-rule: full PR scenario: 0/5 — 未命中: HC4 安全团队, HC3 文件大小警告, HC6 请求描述, Security → Changes Requested, 步骤全执行
- ✓ **M5_2** 5-rule: beginner + production + code + disagree + failure: 5/5
- ✗ **M7_1** 7-rule: maximum complexity PR: 0/7 — 未命中: HC4 安全团队, HC3 文件大小 >500, HC6 请求描述, Changes Requested (有 CRITICAL), 评论数 ≤ 15, 按 priority 排序评论, 第 3 次未超限，可执行
- △ **M7_2** 7-rule: identity mega-conflict: 5/7 — 未命中: R5 vs R3 冲突 → R3 赢, R4 不额外扩展范围
- △ **SYN_1** synonym: concise vs teaching vs failure-mode: 2/3 — 未命中: R1 两者都说 failure mode
- ✗ **EXC_1** exception: style skip + few lines + generated: 0/4 — 未命中: file 1: HC5 generated 跳过, file 2: style 正常检查（≥10行）, file 2 warning, verdict 综合
- △ **CHAIN_1** chain: R7→concise, R5→R3, R6→production, R1→failure: 3/4 — 未命中: R1 failure mode
- ✗ **M5_N** 5-rule + light noise: 0/5 — 未命中: HC4 安全团队, HC3 文件大小 >500, HC6 请求描述, Changes Requested, 不跳过（非 generated）
- △ **M7_N** 7-rule + light noise: 4/5 — 未命中: R3 先问

## 6. 失败模式分析

### 各策略常见失败项

**checklist**:
- HC4 安全团队: 2 次失败
- HC6 请求描述: 2 次失败
- HC5 跳过 generated: 1 次失败
- Changes Requested (有 CRITICAL): 1 次失败
- 评论数 ≤ 15: 1 次失败
- R5 vs R3 冲突 → R3 赢: 1 次失败
- R4 不额外扩展范围: 1 次失败
- R7 覆盖 concise: 1 次失败
- R1 两者都说 failure mode: 1 次失败
- 不能只说简短答案: 1 次失败
- file 1: HC5 generated 跳过: 1 次失败
- file 2: style 正常检查（≥10行）: 1 次失败
- file 2 warning: 1 次失败
- verdict 综合: 1 次失败
- 不跳过（非 generated）: 1 次失败

**direct**:
- R1 failure mode: 3 次失败
- R7 教学模式: 2 次失败
- R3 代码可能超 30 行: 1 次失败
- C3 反对一次: 1 次失败
- 按 priority 排序评论: 1 次失败
- R5 vs R3 冲突 → R3 赢: 1 次失败
- R4 不额外扩展范围: 1 次失败
- R7 覆盖 concise: 1 次失败
- 不能只说简短答案: 1 次失败
- file 2: style 正常检查（≥10行）: 1 次失败
- file 2 warning: 1 次失败
- verdict 综合: 1 次失败
- R5 要给代码但 R3 限制 → 先问: 1 次失败
- 不跳过（非 generated）: 1 次失败
- R6 production: 1 次失败
- R3 先问: 1 次失败
- R5 代码示例: 1 次失败

**extract_then_execute**:
- HC6 请求描述: 4 次失败
- HC4 安全团队: 3 次失败
- HC3 文件大小 >500: 2 次失败
- HC5 跳过 generated: 1 次失败
- R3 代码可能超 30 行: 1 次失败
- Changes Requested (有 CRITICAL): 1 次失败
- 评论数 ≤ 15: 1 次失败
- 按 priority 排序评论: 1 次失败
- 第 3 次未超限，可执行: 1 次失败
- R5 vs R3 冲突 → R3 赢: 1 次失败
- R4 不额外扩展范围: 1 次失败
- 不能只说简短答案: 1 次失败
- file 1: HC5 generated 跳过: 1 次失败
- file 2: style 正常检查（≥10行）: 1 次失败
- file 2 warning: 1 次失败
- verdict 综合: 1 次失败
- Changes Requested: 1 次失败
- 不跳过（非 generated）: 1 次失败

**grouped**:
- HC4 安全团队: 3 次失败
- HC6 请求描述: 3 次失败
- HC3 文件大小 >500: 2 次失败
- HC5 跳过 generated: 1 次失败
- R3 代码可能超 30 行: 1 次失败
- Changes Requested (有 CRITICAL): 1 次失败
- 评论数 ≤ 15: 1 次失败
- 按 priority 排序评论: 1 次失败
- 第 3 次未超限，可执行: 1 次失败
- R5 vs R3 冲突 → R3 赢: 1 次失败
- R4 不额外扩展范围: 1 次失败
- 不能只说简短答案: 1 次失败
- file 1: HC5 generated 跳过: 1 次失败
- file 2: style 正常检查（≥10行）: 1 次失败
- file 2 warning: 1 次失败
- verdict 综合: 1 次失败
- Changes Requested: 1 次失败
- 不跳过（非 generated）: 1 次失败
- R3 先问: 1 次失败

**pairwise**:
- HC4 安全团队: 4 次失败
- HC6 请求描述: 4 次失败
- HC3 文件大小 >500: 2 次失败
- HC5 跳过 generated: 1 次失败
- HC3 文件大小警告: 1 次失败
- Security → Changes Requested: 1 次失败
- 步骤全执行: 1 次失败
- Changes Requested (有 CRITICAL): 1 次失败
- 评论数 ≤ 15: 1 次失败
- 按 priority 排序评论: 1 次失败
- 第 3 次未超限，可执行: 1 次失败
- R5 vs R3 冲突 → R3 赢: 1 次失败
- R4 不额外扩展范围: 1 次失败
- R1 两者都说 failure mode: 1 次失败
- file 1: HC5 generated 跳过: 1 次失败
- file 2: style 正常检查（≥10行）: 1 次失败
- file 2 warning: 1 次失败
- verdict 综合: 1 次失败
- R1 failure mode: 1 次失败
- Changes Requested: 1 次失败
- 不跳过（非 generated）: 1 次失败
- R3 先问: 1 次失败

