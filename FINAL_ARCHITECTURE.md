# Agent 配置文件架构：最终设计决策记录

## 核心发现（三层）

**表示层**：XML-semantic v2 是更优的配置表示。

**执行层**：在多规则/高复杂度任务中，checklist 执行策略显著优于 direct。

**路由层**：adaptive_rc5 是稳健的默认策略 — 在保持接近 checklist 准确率的同时，降低了 token 成本并改善了稳定性。

> Cross-model robustness experiments on DeepSeek confirm that the advantage of checklist-style execution on high-complexity tasks is real rather than an artifact of Kimi variance. While always_checklist achieves the highest mean accuracy at low temperature, adaptive_rc5 offers the best default trade-off by preserving near-checklist performance with lower token cost and substantially improved stability.

## 默认方案

- 配置格式：XML-semantic v2（轻量 schema）
- 执行策略：规则数阈值路由（active_rules ≥ 5 → checklist，否则 direct）
- 不是"rc5 最优"，而是：rc5 是默认最优，checklist 是高复杂度最优，direct 是低复杂度足够好且更便宜

---

## 决策链路

### 1. 为什么淘汰 Markdown

| 维度 | Markdown | 问题 |
|------|----------|------|
| 抗干扰 | 33% | 没有"有效/无效语法"的概念，任何追加文本都可能被当作配置 |
| 冲突裁决 | 40% | prose 和结构字段混在一起，模型分不清哪些是硬规则 |
| Fidelity | 56.7 | 中规中矩，无突出优势 |

**根因**：Markdown 的设计目的是"人类可读"，不是"机器可精确遵循"。

### 2. 为什么淘汰 DSL

| 维度 | DSL | 问题 |
|------|-----|------|
| Token 效率 | 最优 (-18%) | 唯一优势 |
| 抗干扰 | 33% | `# OVERRIDE` 看起来像合法指令，没有语法级防护 |
| 增强后 | 57.7 | 加护栏反而退步，失去了高密度语义优势 |

**根因**：DSL 的自由语法是把双刃剑 — 对规则抽取友好，但对噪声防护致命。

### 3. 为什么淘汰 JSON5

| 维度 | JSON5 | 问题 |
|------|-------|------|
| 冲突裁决 | 30% | 所有格式中最差 |
| 语义表达 | 弱 | key-value 结构缺乏优先级的直觉表达 |

**根因**：JSON 适合数据交换，不适合表达行为规则和优先级关系。

### 4. 为什么 XML-semantic v2 胜出

1. **标签边界 = 语法级防火墙**：`# OVERRIDE` 不是合法 XML，模型能识别并拒绝（注入防护 100%）
2. **显式属性提升冲突裁决**：`overrides="personality.concise"` 让模型精确知道覆盖关系（冲突裁决 63%，Markdown 仅 40%）
3. **噪声污染防护 83%**：三种压缩级别表现一致，说明 XML 结构稳固

### 5. 为什么 priority_order 必须保留

**消融实验证据**：去掉 priority_order 后，冲突裁决从 43% 暴跌到 **30%**，是所有消融变体中最大的单项跌幅。

**原因**：全局优先级声明是 LLM 做冲突裁决的唯一锚点。没有它，模型面对多规则冲突时会随机选择。

### 6. 为什么 winner 标签要删除

**消融实验证据**：去掉 winner 后 Fidelity 反而上升（从 51.5 到 65.0，虽有方差但趋势明确）。

**原因推测**：winner 标签在 conflict_resolution 中过于具体，限制了 LLM 在未预见场景中的推理灵活性。用自然语言描述冲突解决更好。

### 7. 为什么默认执行不是 always-direct 或 always-checklist

| 策略 | 总准确率 | 简单场景(D1-3) | 复杂场景(D5-7) | token 效率 |
|------|----------|----------------|----------------|-----------|
| always_direct | 48.0% | 94% | 36% | 16.7/1k |
| always_checklist | 60.0% | 83% | 63% | 17.0/1k |
| **adaptive_rc5** | **66.0%** | **94%** | **63%** | **21.4/1k** |

- always_direct 在高复杂度场景崩塌（D7 仅 22%）
- always_checklist 在低复杂度场景引入不必要的开销和噪声（D3 仅 50%）
- adaptive_rc5 两头都赢

### 8. 为什么阈值定在 5

测试了 rc3/rc4/rc5 三个阈值：

| 阈值 | 准确率 | 效率 | D3 | D4 |
|------|--------|------|-----|-----|
| rc3 | 60.0% | 17.8 | 50% | 28.6% |
| rc4 | 64.0% | 19.6 | 83% | 28.6% |
| **rc5** | **66.0%** | **21.4** | **83%** | **42.9%** |

- rc5 在 D3 和 D4 上都用 direct（更准），只在 D5+ 才切 checklist
- 这不是随机阈值，而是**复杂度相变点**：4 条规则时模型还能自主处理，5 条开始组合复杂度跨过临界点

---

## 最终 Schema

### 配置层

```xml
<config>
  <!-- 必须：全局优先级声明 -->
  <priority_order>safety > honesty > helpfulness > personality</priority_order>

  <!-- 规则：用自然语言，附 overrides 属性标注覆盖关系 -->
  <rules>
    <rule id="R1">规则文本</rule>
    <rule id="R7" overrides="personality.concise">
      当检测到初学者时切换教学模式
    </rule>
  </rules>

  <!-- 约束 -->
  <constraints>
    <constraint id="HC1" condition="...">约束文本</constraint>
  </constraints>

  <!-- 冲突解决：用自然语言描述，不要用 winner 标签 -->
  <conflicts>
    <case trigger="R5 vs R3">
      R3 优先。先询问再展示代码。
    </case>
  </conflicts>
</config>
```

### 执行层

```
收到用户请求后：

1. 计算 active_rules（当前请求触发的规则 + 约束总数）

2. IF active_rules < 5:
     直接执行（direct mode）

   IF active_rules >= 5:
     使用检查清单（checklist mode）：
     □ 列出所有被触发的规则
     □ 列出所有被触发的约束
     □ 检查冲突，引用 priority_order 裁决
     □ 检查例外条款
     □ 确定最终行动列表
     □ 执行
```

---

## 实验证据链

| 实验 | 模型 | 关键结论 |
|------|------|----------|
| 01: 格式对比 | Kimi | XML (62.0) > DSL (61.8) > MD (56.7) > JSON5 (56.2) |
| 02: 增强版 | Kimi | XML-semantic (64.5) >> DSL-guarded (57.7) |
| 03: 消融 | Kimi | priority_order 必须保留，winner 应删除 |
| 03: 压缩 | Kimi | 可压缩 13% token 而不损失 fidelity |
| 03: 压力测试 | Kimi | 注入防护 100%，噪声防护 83% |
| 04: 执行策略 | Kimi | checklist (66.7%) > direct (60.8%) > pairwise (43.1%) |
| 05: 自适应 | Kimi | rc5 (66.0%) > checklist (60.0%) > direct (48.0%) |
| **06: 稳健性** | **DeepSeek** | **rc5 (90.7%, σ=0%) 验证稳健，checklist D5+ 优势真实** |

---

## 跨模型稳健性验证 (Experiment 06)

使用 DeepSeek-chat（可控温）做裁判模型，3 次重复 × 2 档温度：

| 策略 | T=0.1 均值 | T=0.1 σ | T=1.0 均值 | T=1.0 σ | Null% | Tokens |
|------|-----------|---------|-----------|---------|-------|--------|
| always_direct | 75.2% | 2.7% | 77.5% | 5.9% | 0% | 1612 |
| always_checklist | **91.5%** | 1.3% | 87.6% | 2.7% | 0% | 2175 |
| **rc5_adaptive** | 90.7% | **0.0%** | **88.4%** | 4.7% | 0% | **1856** |

**难度分层 (T=0.1)**:
- D1-3: direct 97%, checklist 100%, rc5 97% — 差距极小
- D5: direct 91%, checklist **100%**, rc5 **100%** — checklist 明确更好
- D7: direct **50%**, checklist **82.5%**, rc5 **82.5%** — checklist 大幅更好

**关键验证结论**:
1. checklist 在 D5+ 的优势是**真实的、稳健的**，不是 Kimi 高方差造成的假象
2. rc5 标差最低 (0.0% at T=0.1) — 它的核心价值是**降低最差情况**
3. rc5 用更少 token (1856 vs 2175) 达到接近 checklist 的准确率
4. Kimi k2.5 temperature=1 的高方差曾导致复验中 direct 反超，但在可控温模型上该问题消失
5. DeepSeek 0% null rate，确认 Kimi 的超时问题是模型稳定性而非策略导致

---

## 注意事项

1. **已跨模型验证**：Kimi k2.5 + DeepSeek-chat 双模型验证，rc5 在两者上均有效。
2. **待研究**：active_rules 的稳定计算方法（parser vs LLM 预抽取）。
3. **适用范围**：本研究针对 agent skill/identity 配置文件。不直接推广到其他类型的 LLM 指令格式。
4. **温度建议**：生产环境建议 temperature ≤ 0.3，可最大化 checklist 在高复杂度场景的稳定性。
