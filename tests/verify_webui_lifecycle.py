#!/usr/bin/env python3
"""LoopDesk WebUI × gateway —— 任务全生命周期前后端接线复验（真实浏览器 + 真实 HTTP）。

断言口径：不是「页面点得动」，而是「前端确实调用了后端，且后端状态反过来改变了界面」。

运行：  .venv/bin/python tests/verify_webui_lifecycle.py
前置：  loopdesk gateway run --port 18792（并已完成 `npm run build`）
产物：  报告 JSON 落在 /tmp/loopdesk-lifecycle/wired_report.json
"""

from __future__ import annotations

import asyncio
import json
import urllib.request

from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:18792"
API = "/api/v1"
PROJECT = "default"

NEW_TASK_DESC = "接通网关后由前端落库的验证任务"
CANVAS_TITLE = "为网关补充限流与熔断策略"

RESULTS: list[tuple[str, bool, str]] = []


def log(step: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((step, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {step}" + (f"   [{detail}]" if detail else ""))


def http(method: str, path: str, payload: dict | None = None):
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


async def main() -> int:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()

        api_calls: list[tuple[str, str]] = []
        console_errors: list[str] = []
        page.on(
            "request",
            lambda r: api_calls.append((r.method, r.url)) if "/api/" in r.url else None,
        )
        page.on(
            "console",
            lambda m: console_errors.append(f"console:{m.text}") if m.type == "error" else None,
        )
        page.on("pageerror", lambda e: console_errors.append(f"pageerror:{e}"))

        def api_hits(method: str, needle: str) -> list[str]:
            return [u for m, u in api_calls if m == method and needle in u]

        async def wait_api(method: str, needle: str, timeout: int = 6000) -> bool:
            waited = 0
            while waited < timeout:
                if api_hits(method, needle):
                    return True
                await page.wait_for_timeout(200)
                waited += 200
            return False

        async def card_ids(column: str) -> list[str]:
            return await page.locator(
                f"[data-column='{column}'] [data-card-id]"
            ).evaluate_all("els => els.map(e => e.dataset.cardId)")

        async def wait_card(column: str, card_id: str, timeout: int = 8000) -> bool:
            waited = 0
            while waited < timeout:
                if card_id in await card_ids(column):
                    return True
                await page.wait_for_timeout(200)
                waited += 200
            return False

        async def badge(column: str) -> int:
            """列头徽标数字 —— 画布基数是 5/4/2/9。"""
            txt = await page.locator(f"[data-column='{column}']").first.locator("span").nth(1).inner_text()
            return int(txt.strip())

        # ---------------- 阶段 0 · 载入与接线存活 ----------------
        await page.goto(BASE + "/", wait_until="load")
        await page.wait_for_timeout(2500)

        root = page.locator("[data-loopdesk-tasks]")
        online = await root.get_attribute("data-loopdesk-online")
        n_tasks = await root.get_attribute("data-loopdesk-tasks")

        hits = api_hits("GET", f"{API}/projects/{PROJECT}/tasks")
        log("01 载入即拉任务快照 GET /api/v1/projects/{id}/tasks", bool(hits), f"命中 {len(hits)} 次")
        log(
            "02 事件总线 SSE GET /api/v1/events 已连接",
            bool(api_hits("GET", f"{API}/events")),
            f"命中 {len(api_hits('GET', f'{API}/events'))} 次",
        )
        log("03 接线状态 data-loopdesk-online = true", online == "true", f"值={online}")
        log("04 后端任务数已进前端 data-loopdesk-tasks", n_tasks == "1", f"值={n_tasks}")

        # ---------------- 阶段 1 · 看板 = 画布种子 ⊕ 后端任务 ----------------
        seeded = {
            cid: await page.locator(f"[data-card-id='{cid}']").count()
            for cid in ("ACME-218", "ACME-201", "ACME-196", "ACME-172")
        }
        log("05 画布种子卡片仍在（设计稿 8 张卡不被后端顶掉）", all(v == 1 for v in seeded.values()), str(seeded))

        n_cols = await page.locator("[data-column]").count()
        log("06 看板仍是四列", n_cols == 4, f"列数={n_cols}")

        doing = await card_ids("doing")
        log("07 后端独有的任务已作为真卡片叠进看板", "task-1aa1af6b" in doing, f"进行中={doing}")

        # ---------------- 阶段 2 · 新建任务落库 ----------------
        await page.locator("button:has-text('新建任务')").first.click()
        await page.wait_for_timeout(500)
        modal_seen = await page.locator("[data-testid='new-task-desc']").count() == 1
        await page.locator("[data-testid='new-task-desc']").fill(NEW_TASK_DESC)
        await page.locator("button:has-text('开始任务')").click()

        created = await wait_api("POST", f"{API}/projects/{PROJECT}/tasks")
        await page.wait_for_timeout(1200)
        board_text = await page.locator("main").inner_text()
        log("08 新建任务面板可见且描述可输入", modal_seen, "描述是真实 textarea，占位符沿用画布 muted 色")
        log("09 「开始任务」→ POST /api/v1/projects/{id}/tasks", created, "请求已发出")
        log("10 新任务出现在看板上", NEW_TASK_DESC in board_text, f"标题={NEW_TASK_DESC}")

        _, body = http("GET", f"{API}/projects/{PROJECT}/tasks")
        titles = [t.get("title") for t in (body.get("tasks") or [])] if isinstance(body, dict) else []
        log("11 HTTP 交叉核对：任务真的落库了", NEW_TASK_DESC in titles, f"后端现有标题={titles}")

        # ---------------- 阶段 3 · 审批门裁决（卡片动作 → 后端 → 看板） ----------------
        await page.locator("[data-card-id='ACME-196'] button:has-text('通过')").click()
        await page.wait_for_timeout(700)
        modal_text = await page.locator("body").inner_text()
        log(
            "12 评审列「通过」→ 打开审批门裁决模态",
            "审批门裁决" in modal_text and "ACME-196" in modal_text,
            "模态显示目标任务",
        )
        await page.locator("textarea").last.fill("E2E：放行并执行")
        await page.locator("button:has-text('确认提交')").click()

        gated = await wait_api("POST", "/gate/decision")
        moved = await wait_card("done", "ACME-196")
        log("13 「确认提交」→ POST /api/v1/tasks/{id}/gate/decision", gated, "请求已发出")
        log("14 后端裁决回写改变了看板列位（评审中 → 已完成）", moved, f"已完成列={await card_ids('done')}")

        b_review, b_done, b_doing = await badge("review"), await badge("done"), await badge("doing")
        log(
            "14b 列头徽标按卡片流动重算（评审中 −1、已完成 +1、进行中 = 基数+后端追加）",
            b_review == 1 and b_done == 10 and b_doing == 6,
            f"待办/进行中/评审中/已完成 = {await badge('todo')}/{b_doing}/{b_review}/{b_done}",
        )

        _, body = http("GET", f"{API}/projects/{PROJECT}/tasks")
        rec = (
            next((t for t in (body.get("tasks") or []) if t.get("id") == "ACME-196"), {})
            if isinstance(body, dict)
            else {}
        )
        log(
            "15 裁决保留任务标题（未被改写成裁决批注）",
            rec.get("title") == CANVAS_TITLE and rec.get("status") == "completed",
            f"title={rec.get('title')!r} status={rec.get('status')}",
        )

        # ---------------- 阶段 4 · SSE 实时性 ----------------
        before = await page.locator("[data-card-id]").count()
        _, body = http(
            "POST",
            f"{API}/projects/{PROJECT}/tasks",
            {"title": "外部 HTTP 注入的 SSE 探针任务", "template": "auto-research"},
        )
        probe_id = (body or {}).get("task", {}).get("id") if isinstance(body, dict) else None
        pushed, waited = False, 0
        while waited < 8000 and probe_id:
            if probe_id in await card_ids("doing"):
                pushed = True
                break
            await page.wait_for_timeout(250)
            waited += 250
        after = await page.locator("[data-card-id]").count()
        log(
            "16 外部 POST 后看板自动刷新（SSE 事件驱动，无需手刷）",
            pushed and after == before + 1,
            f"卡片 {before} → {after}，探针={'上板' if pushed else '未出现'}",
        )

        # ---------------- 阶段 5 · 右栏 / 详情 / 折叠 ----------------
        await page.locator("[data-card-id='ACME-201']").click()
        await page.wait_for_timeout(500)
        aside_n = await page.locator("aside").count()
        insp = await page.locator("aside").nth(1).inner_text()
        log("17 单击卡片 → 右栏跟随选中（ACME-201）", aside_n == 2 and "ACME-201" in insp, f"aside={aside_n}")

        await page.locator("[data-testid='inspector-close']").click()
        await page.wait_for_timeout(500)
        log("18 右栏 ✕ 折叠生效", await page.locator("aside").count() == 1, "aside 2 → 1")

        await page.keyboard.press("Meta+b")
        await page.wait_for_timeout(500)
        log("19 ⌘B 展开右栏", await page.locator("aside").count() == 2, "aside 1 → 2")

        await page.locator("button:has-text('查看详情')").first.click()
        await page.wait_for_timeout(900)
        detail = await page.locator("main").inner_text()
        in_detail = await page.locator("[data-testid='detail-back']").count() == 1
        cols_in_detail = await page.locator("[data-column]").count()
        log(
            "20 右栏「查看详情 →」进任务详情（看板被详情取代，带上被选中任务 id）",
            in_detail and cols_in_detail == 0 and "ACME-201" in detail,
            f"返回控件={in_detail} 详情里的看板列={cols_in_detail}",
        )

        await page.locator("[data-testid='detail-back']").click()
        await page.wait_for_timeout(700)
        back_cols = await page.locator("[data-column]").count()
        back_controls = await page.locator("[data-testid='detail-back']").count()
        log(
            "21 详情 ✕ 返回看板（四列回来，详情退场）",
            back_cols == 4 and back_controls == 0,
            f"列数={back_cols} 残留返回控件={back_controls}",
        )

        # ---------------- 阶段 6 · 控制台 ----------------
        log("22 控制台零错误 / 零 pageerror", not console_errors, f"{console_errors[:3]}")

        await page.screenshot(path="/tmp/loopdesk-lifecycle/wired_board.png")
        await browser.close()

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print(f"\n=== {passed}/{total} 通过 ===")
    print(f"本次走查前端发出的 /api 请求：{len(api_calls)} 条（验收基线：> 0）")
    for m, u in api_calls:
        print(f"  {m:4s} {u.replace(BASE, '')}")

    json.dump(
        {
            "passed": passed,
            "total": total,
            "results": [{"step": s, "ok": o, "detail": d} for s, o, d in RESULTS],
            "api_calls": [{"method": m, "url": u} for m, u in api_calls],
            "console_errors": console_errors,
        },
        open("/tmp/loopdesk-lifecycle/wired_report.json", "w"),
        ensure_ascii=False,
        indent=2,
    )
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
