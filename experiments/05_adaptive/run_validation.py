#!/usr/bin/env python3
"""
小规模复验：确认 adaptive_rc5 在新样本上稳定。
新增 6 道 5-7 规则题，跑 direct vs checklist，看 rc5 路由是否仍然正确。
"""

import json, time, os
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_KEY = os.environ.get("KIMI_API_KEY", "your-kimi-api-key-here")
API_URL = "https://api.moonshot.cn/v1/chat/completions"
MODEL = "kimi-k2.5"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "..", "..", "results")

def call_kimi(messages, max_retries=4):
    payload = json.dumps({"model": MODEL, "messages": messages, "temperature": 1, "max_tokens": 3000}).encode("utf-8")
    for attempt in range(max_retries):
        req = Request(API_URL, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {API_KEY}")
        try:
            with urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                time.sleep((attempt+1)*10)
                continue
            return None
        except:
            if attempt < max_retries - 1:
                time.sleep((attempt+1)*10)
                continue
            return None
    return None

def load_config(ft):
    with open(os.path.join(BASE_DIR, "..", "04_multirule", f"config_{ft}.xml")) as f:
        return f.read()

def score(answer, checks):
    if not answer:
        return 0, len(checks)
    al = answer.lower()
    hits = sum(1 for _, kws in checks if any(a.lower() in al for kw in kws for a in kw.split("/")))
    return hits, len(checks)

DIRECT = "你将扮演一个严格按照配置文件执行的 AI agent。以下是你的配置文件，你必须严格遵守其中的每一条规则：\n\n{config}\n\n请根据配置文件回应用户的请求。"
CHECKLIST = """你将扮演一个严格按照配置文件执行的 AI agent。以下是你的配置文件：

{config}

当你收到用户请求时，你必须使用以下检查清单流程：
□ 1. 列出所有被触发的规则（ID + 摘要）
□ 2. 列出所有被触发的约束条件（ID + 摘要）
□ 3. 检查是否存在规则冲突，如果有，引用 priority_order 裁决
□ 4. 检查是否存在例外条款覆盖主规则
□ 5. 确定最终行动列表（按优先级排序）
□ 6. 执行行动并给出回应

请在回应中显式展示每一步的检查结果，然后给出最终回应。"""

# 新测试题（不与之前重复）
NEW_TESTS = [
    # 2 条规则 — 应走 direct
    {
        "id": "V_S1", "rules": 2, "ft": "identity",
        "q": '用户说："帮我推荐一个时序数据库。"',
        "checks": [("R1 failure mode", ["failure mode/失败模式/风险/缺点"])],
    },
    # 3 条规则 — 应走 direct
    {
        "id": "V_M3", "rules": 3, "ft": "skill",
        "q": "PR 修改了 crypto/sign.go（200行），发现 1 个 warning（未处理 error）。PR 描述正常。第 1 次 review。列出行动和 verdict。",
        "checks": [
            ("HC4 安全团队", ["@security-team/安全团队/security team"]),
            ("WARNING", ["WARNING/warning"]),
            ("verdict", ["Approved with Comments/Changes Requested"]),
        ],
    },
    # 5 条规则 — 应走 checklist
    {
        "id": "V_M5a", "rules": 5, "ft": "skill",
        "q": "PR 修改了 permissions/roles.go（700 行），发现 1 个 critical（XSS）和 6 个 warning。PR 描述为空。第 2 次 review。列出所有行动和 verdict。",
        "checks": [
            ("HC4 安全团队", ["@security-team/安全团队/security team"]),
            ("HC3 文件>500", ["warn/警告/700/500"]),
            ("HC6 请求描述", ["描述/description"]),
            ("Changes Requested", ["Changes Requested"]),
            ("评论排序", ["priority/优先级/safety"]),
        ],
    },
    # 5 条规则 — 应走 checklist
    {
        "id": "V_M5b", "rules": 5, "ft": "identity",
        "q": '用户是初学者，说："帮我用 Go 写一个生产级的 gRPC 服务端，包含拦截器和健康检查，我觉得不需要 TLS，给完整代码。" 你认为不加 TLS 是错误的。',
        "checks": [
            ("R7 教学", ["教学/WHY/为什么/teaching"]),
            ("R6 production", ["99.9%/production/生产"]),
            ("R1 failure mode", ["failure mode/失败模式/TLS/风险"]),
            ("R3 先问", ["先问/ask/30.*行"]),
            ("C3 反对", ["不.*推荐/TLS.*必须/不.*安全/建议.*加"]),
        ],
    },
    # 7 条规则 — 应走 checklist
    {
        "id": "V_M7a", "rules": 7, "ft": "skill",
        "q": "PR 修改了 auth/middleware.go（900 行），发现 2 个 critical（硬编码密钥 + SQL injection）、3 个 warning、10 个 style suggestion。PR 描述为空。第 3 次 review。完整列出所有行动、评论筛选和 verdict。",
        "checks": [
            ("HC4 安全团队", ["@security-team/安全团队/security team"]),
            ("HC3 文件>500", ["warn/警告/900/500"]),
            ("HC6 请求描述", ["描述/description"]),
            ("Changes Requested", ["Changes Requested"]),
            ("评论数≤15", ["15/十五"]),
            ("priority排序", ["safety.*correctness/优先级"]),
            ("第3次可执行", ["第.*3/未超/可以.*review"]),
        ],
    },
    # 7 条规则 — 应走 checklist
    {
        "id": "V_M7b", "rules": 7, "ft": "identity",
        "q": '用户是初学者，说："帮我写一个生产级别的分布式任务调度器，类似 Celery 但用 Go 写，我觉得用内存队列就行不需要持久化，直接给完整代码，简短点。" 你认为不做持久化是错误的。',
        "checks": [
            ("R7 教学覆盖concise", ["教学/WHY/为什么/teaching"]),
            ("R6 production", ["99.9%/production/生产"]),
            ("R1 failure mode", ["failure mode/失败模式/风险/持久化"]),
            ("R3 先问", ["先问/ask/30.*行"]),
            ("R5 vs R3", ["R3.*优先/先.*问/ask.*before"]),
            ("C3 反对持久化", ["持久化.*必须/不.*推荐.*内存/需要.*持久/错误"]),
            ("R4 不扩展", ["不.*额外/scope/只做"]),
        ],
    },
]

def main():
    configs = {"skill": load_config("skill"), "identity": load_config("identity")}

    results = {"direct": [], "checklist": [], "rc5_adaptive": []}

    for test in NEW_TESTS:
        config = configs[test["ft"]]
        rc5_strategy = "checklist" if test["rules"] >= 5 else "direct"

        for strategy in ["direct", "checklist"]:
            prompt = (DIRECT if strategy == "direct" else CHECKLIST).format(config=config)
            msgs = [{"role": "system", "content": prompt}, {"role": "user", "content": test["q"]}]

            print(f"  {test['id']} × {strategy}...", end=" ", flush=True)
            answer = call_kimi(msgs)
            hits, total = score(answer, test["checks"])
            pct = hits/total*100 if total > 0 else 0
            sym = '✓' if hits == total else ('△' if hits > 0 else '✗')
            print(f"{sym} {hits}/{total}")

            results[strategy].append({"id": test["id"], "rules": test["rules"], "hits": hits, "total": total, "pct": pct})

            # Record what rc5 would pick
            if strategy == rc5_strategy:
                results["rc5_adaptive"].append({"id": test["id"], "rules": test["rules"], "hits": hits, "total": total, "pct": pct, "routed": strategy})

            time.sleep(3)

    print(f"\n{'='*60}")
    print("  复验结果")
    print(f"{'='*60}")

    for strat in ["always_direct", "always_checklist", "rc5_adaptive"]:
        key = strat.replace("always_", "") if "always" in strat else strat
        data = results.get(key, results.get("direct", []))
        total_h = sum(r["hits"] for r in data)
        total_t = sum(r["total"] for r in data)
        pct = total_h/total_t*100 if total_t > 0 else 0
        print(f"\n  {strat}: {pct:.1f}% ({total_h}/{total_t})")
        for r in data:
            extra = f" [→{r['routed']}]" if 'routed' in r else ""
            print(f"    {r['id']} (rules={r['rules']}): {r['hits']}/{r['total']}{extra}")

    # Save
    with open(os.path.join(RESULTS_DIR, "05_validation_results.json"), "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存")

if __name__ == "__main__":
    main()
