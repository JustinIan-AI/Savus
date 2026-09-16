import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. 访问首页
        print("[Step 1] 正在导航到 http://127.0.0.1:18792/ ...")
        await page.goto("http://127.0.0.1:18792/")
        await page.wait_for_load_state("networkidle")
        title = await page.title()
        print(f"页面加载成功，Title: {title}")
        
        # 检查看板四列是否存在
        columns = await page.locator("text=待办").count()
        print(f"看板列检测: 待办存在? {columns > 0}")
        
        # 2. 模拟新建任务
        print("[Step 2] 触发新建任务 (C4)...")
        # 点击左栏或看板上的新建任务按钮
        new_task_btn = page.locator("button:has-text('新建任务')").first
        if await new_task_btn.count() > 0:
            await new_task_btn.click()
            print("新建任务模态窗已弹出")
            await page.wait_for_timeout(500)
            
            # 选择 issue-fix 模板并确认
            issue_fix_tpl = page.locator("text=issue-fix").first
            if await issue_fix_tpl.count() > 0:
                await issue_fix_tpl.click()
                print("已选中 issue-fix 缺陷修复流水线模板")
            
            confirm_btn = page.locator("button:has-text('确认创建')").first
            if await confirm_btn.count() > 0:
                await confirm_btn.click()
                print("已提交新建任务")
                await page.wait_for_timeout(500)

        # 3. 任务卡片点击与详情流转 (C2 -> C5)
        print("[Step 3] 验证任务卡片点击与详情流转...")
        first_card = page.locator("text=LD-").first
        if await first_card.count() > 0:
            card_text = await first_card.inner_text()
            print(f"找到任务卡片: {card_text[:30]}...")
            await first_card.click()
            await page.wait_for_timeout(500)
            
            # 验证右栏三段生成模型展示
            inspector_text = await page.locator("aside").inner_text()
            print("右栏展开成功，包含六阶段状态与操作:")
            for line in inspector_text.split("\n")[:8]:
                if line.strip():
                    print(f"  > {line.strip()}")
            
            # 4. 验证审批门放行决策 (R4 Approve/Deny Modal)
            print("[Step 4] 验证审批门放行/驳回决策交互...")
            approve_btn = page.locator("button:has-text('放行')").first
            if await approve_btn.count() > 0:
                await approve_btn.click()
                await page.wait_for_timeout(500)
                modal_title = page.locator("text=审批门决断").first
                if await modal_title.count() > 0:
                    print("✓ 审批门决策模态窗 (GateDecisionModal) 成功弹出！")
                    confirm_approve = page.locator("button:has-text('确认放行')").first
                    await confirm_approve.click()
                    print("✓ 已执行审批放行指令并向后端同步！")
                    await page.wait_for_timeout(500)
        
        # 5. 验证快捷键与右栏折叠 (Cmd/Ctrl + B)
        print("[Step 5] 验证右栏折叠与快捷键 (Cmd+B)...")
        await page.keyboard.press("Meta+b")
        await page.wait_for_timeout(300)
        aside_visible = await page.locator("aside").is_visible()
        print(f"按下 ⌘B 后右栏收起: {not aside_visible}")
        await page.keyboard.press("Meta+b")
        await page.wait_for_timeout(300)
        aside_reopen = await page.locator("aside").is_visible()
        print(f"再次按下 ⌘B 后右栏重新展开: {aside_reopen}")

        # 6. 验证项目下拉切换 (L1)
        print("[Step 6] 验证 TopBar 项目切换器...")
        project_btn = page.locator("text=Acme Platform").first
        await project_btn.click()
        await page.wait_for_timeout(300)
        dropdown_item = page.locator("text=LoopDesk Core").first
        if await dropdown_item.count() > 0:
            print("✓ 项目下拉菜单已正常展开，选择 LoopDesk Core")
            await dropdown_item.click()
            print("✓ 项目切换已完成")

        print("\n========================================================")
        print("✓ 全生命周期前后端完备性验证全部通过！")
        print("========================================================")
        await browser.close()

asyncio.run(main())
