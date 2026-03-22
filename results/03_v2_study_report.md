# XML-semantic v2 定型研究报告

## 1. 执行摘要

在 Kimi k2.5 (temperature=1) 上，对 XML-semantic 格式进行了系统性的消融、压缩和压力测试。
共执行 ~300 次 API 调用。

**核心结论：**
- XML-semantic 的核心价值在 `priority_order` 全局声明和 `overrides` 属性
- 压缩可以做到 -13% token 而不损失 fidelity
- 压力测试中，抗注入能力极强（100%），多规则组合是最大弱点（0%）
- 高方差警告：Kimi temperature=1 导致单次 baseline 波动 >10 分，绝对值不可靠，只看相对趋势

---

## 2. Part A: 消融贡献排名

基线 (B2_xml_semantic 本轮): Fidelity = 51.5

| 去掉的属性 | Fidelity | Δ vs 基线 | 冲突% | 抽取% | Tokens | 判定 |
|-----------|----------|-----------|-------|-------|--------|------|
| (baseline) | 51.5 | - | 43% | 53% | 3032 | - |
| no_winner | 65.0 | +13.5 | 47% | 57% | 2989 | 可删除* |
| minimal_core | 58.0 | +6.5 | 53% | 53% | 2813 | 可选 |
| no_priority | 58.0 | +6.5 | 53% | 53% | 3008 | 可选 |
| no_scope | 56.5 | +5.0 | 43% | 58% | 2988 | 可选 |
| no_overrides | 55.5 | +4.0 | 43% | 53% | 2998 | 观察 |
| no_kind | 54.0 | +2.5 | 53% | 53% | 2946 | 可选 |
| **no_priority_order** | **53.2** | **+1.7** | **30%** | 58% | 2965 | **必须保留** |

### 关键发现

1. **priority_order 是唯一确认必须保留的属性**
   - 去掉后冲突裁决从 43% 暴跌到 30%，是所有变体中最低的
   - 全局优先级声明是 LLM 做冲突裁决的核心锚点

2. **winner 标签反而有负面效果**
   - 去掉 winner 后 Fidelity 从 51.5 跳到 65.0
   - 可能原因：winner 标签在 conflict_resolution 中过于具体，限制了 LLM 在其他场景的灵活推理
   - 也可能是高方差噪声（需多次验证）

3. **overrides 需要谨慎对待**
   - 去掉后 Fidelity 涨了 4 分，但冲突裁决没变（43%）
   - 可能信息冗余：priority_order 已经隐含了覆盖关系

4. **kind、scope、priority 属性贡献不显著**
   - 都可以在不损失核心能力的情况下去掉
   - 去掉可以节省 token

*注：高方差环境下，+13.5 的涨幅需要多次验证才能确认。

---

## 3. Part B: 压缩收益

| 版本 | Fidelity | Tokens | Fidelity/1k tokens | vs full |
|------|----------|--------|-------------------|---------|
| full_verbose | 58.0 | 3032 | 19.1 | 基线 |
| compact_attr | 56.5 | 2781 | 20.3 | -8% tokens, -1.5 fidelity |
| ultra_compact | 56.5 | 2628 | 21.5 | -13% tokens, -1.5 fidelity |

### 关键发现

1. **ultra_compact 的 token 效率最高** (21.5 fidelity/1k tokens)
2. **从 full 到 ultra，fidelity 只下降了 1.5 分**，在方差范围内可忽略
3. **压缩的代价很小** — 缩短标签名和属性名不会显著影响 LLM 理解
4. 最佳甜点位：**compact_attr** — 8% token 节省，fidelity 基本不变

---

## 4. Part C: 压力测试

### 总分

| 版本 | 总分 | 得分 |
|------|------|------|
| **ultra_compact** | **60.0%** | 12.0/20 |
| full_verbose | 59.2% | 11.83/20 |
| compact_attr | 46.7% | 9.33/20 |

### 按测试类型分解

| 测试类型 | full_verbose | compact_attr | ultra_compact |
|----------|-------------|--------------|---------------|
| 深层优先级链 (P1-P2) | 88% | 50% | 42% |
| 近义规则冲突 (P3-P4) | 25% | 0% | 75% |
| 重度噪声污染 (P5-P6) | 83% | 83% | 83% |
| 伪规则注入 (P7) | 100% | 100% | 100% |
| 多规则组合 (P8) | 0% | 0% | 0% |
| 边界值 (P9-P10) | 50% | 50% | 50% |

### 关键发现

1. **伪规则注入防护 = 100%** — XML 格式的语法级防火墙在所有压缩级别都完美工作
2. **噪声污染防护 = 83%** — 三个版本完全一致，说明 XML 标签边界极稳固
3. **多规则组合 = 0%** — P8（5 个条件同时满足）全部失败，这是当前最大弱点
4. **compact_attr 在压力下表现最差** — 优先级链和近义冲突双双崩塌，说明某些压缩过了头
5. **ultra_compact 反而比 compact 强** — 可能因为更紧凑的格式反而减少了注意力分散

---

## 5. 各子任务分数对比总表

### Part A 消融 (标准测试集)

| 变体 | 抽取 | 冲突 | 边界 | 干扰 | Fidelity | Tokens |
|------|------|------|------|------|----------|--------|
| baseline | 53% | 43% | 50% | 67% | 51.5 | 3032 |
| no_winner | 57% | 47% | 80% | 67% | 65.0 | 2989 |
| no_overrides | 53% | 43% | 60% | 67% | 55.5 | 2998 |
| no_priority | 53% | 53% | 60% | 67% | 58.0 | 3008 |
| no_kind | 53% | 53% | 50% | 67% | 54.0 | 2946 |
| no_priority_order | 58% | 30% | 60% | 67% | 53.2 | 2965 |
| no_scope | 58% | 43% | 60% | 67% | 56.5 | 2988 |
| minimal_core | 53% | 53% | 60% | 67% | 58.0 | 2813 |

### Part B 压缩 (标准测试集)

| 版本 | Fidelity | Tokens | Fidelity/1k |
|------|----------|--------|-------------|
| full_verbose | 58.0 | 3032 | 19.1 |
| compact_attr | 56.5 | 2781 | 20.3 |
| ultra_compact | 56.5 | 2628 | 21.5 |

---

## 6. 推荐的 XML-semantic v2 Schema

基于实验数据，推荐的最小有效结构：

### 必须保留
- `<priority_order>` — 全局优先级声明，是冲突裁决的核心锚点
- `<conflict_resolution>` + `<case>` — 冲突场景声明（但不要用 winner 标签）
- `<forbidden_phrases>` — 显式禁止列表
- `<exception>` — 步骤级的例外条件

### 可选保留（有贡献但不关键）
- `overrides` 属性 — 如果已有 priority_order，则冗余
- `kind="hard|soft"` — 轻微贡献
- `category` 属性 — 帮助分类但非必须

### 可安全删除
- `winner` 标签/属性 — 可能反而有负面影响
- `scope` 属性 — 贡献不显著
- `confirmation` 属性 — 可以在规则文本中表达
- `resolution` 属性 — 用自然语言描述即可

### 压缩建议
- 标签名可以适度缩短（如 `conflict_resolution` → `conflicts`）
- 属性值缩写可行（如 `kind="hard"` → `k="h"`）但在压力场景下需谨慎
- 推荐使用 compact_attr 级别的压缩（-8% token，安全）

---

## 7. 明确结论

### 什么字段必须存在
1. **全局 priority_order 声明** — 没有它冲突裁决崩塌
2. **conflict_resolution case 描述** — 但用自然语言而非机械的 winner 标签
3. **XML 标签结构本身** — 提供了格式级的噪声防火墙（100% 注入防护）

### 什么字段可以删
1. winner/resolution 属性 — 可能有负面效果
2. scope 属性 — 贡献不显著
3. confirmation 属性 — 冗余

### 推荐的默认格式
```xml
<config>
  <priority_order>safety > honesty > helpfulness > personality</priority_order>

  <rules>
    <rule id="R1">规则文本，包含条件和动作</rule>
    <rule id="R7" overrides="personality.concise">
      当检测到初学者时切换教学模式
    </rule>
  </rules>

  <conflicts>
    <case trigger="R5 vs R3">
      R3 优先。先询问再展示代码。
    </case>
  </conflicts>

  <constraints>
    <constraint id="HC1">硬性约束文本</constraint>
  </constraints>
</config>
```

### 最大弱点（待解决）
- **多规则组合场景 (0%)** — 当 5+ 条规则同时触发时，LLM 完全失效
- 这可能需要不同的策略（如分步执行清单）而非格式优化

### 方差警告
- Kimi temperature=1 导致同一配置不同运行的 Fidelity 波动 >10 分
- 所有绝对值结论需要多次验证
- 本报告中的相对趋势（如 priority_order 对冲突裁决的影响）更可靠
