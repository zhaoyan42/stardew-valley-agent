# 星露谷物语 AI 决策与自动化控制系统设计文档 (Spec)

## 1. 项目愿景
构建一个能够实现“全自动决策”的星露谷物语 AI 代理。该系统不仅能执行基础的农场操作，还能通过视觉和数据感知环境，自主规划每日行程，并根据历史经验（自我演进）优化战术决策。

## 2. 系统架构
系统采用“战略-战术”双层架构，通过 MCP (Model Context Protocol) 进行通信。

### 2.1 战略层 (Strategic Brain - Python)
*   **核心组件**：基于 LLM (如 Claude 3.5 Sonnet / GPT-4o) 的决策引擎。
*   **职责**：
    *   **每日规划**：早上 6:00 AM 获取状态，生成当日任务队列。
    *   **突发处理**：响应战术层传回的特殊事件（如：体力耗尽、发现宝箱）。
    *   **复盘演进**：深夜总结当日表现，更新长期记忆，优化 `tactics.json`。
*   **记忆系统 (混合模式)**：
    *   **层级知识库 (OpenViking 风格)**：存储静态百科（Wiki），采用 `viking://wiki/` 路径减少 Token 消耗。
    *   **动态事实库 (Mem0 + ChromaDB)**：存储玩家偏好、历史教训和 NPC 关系，支持语义检索。

### 2.2 战术层 (Tactical Spine - C# SMAPI Mod)
*   **核心组件**：星露谷物语 SMAPI 插件。
*   **职责**：
    *   **环境感知**：捕获游戏截图并提取结构化 JSON 数据。
    *   **原子动作库 (Atomic Actions)**：
        *   `Interact(x, y)`: 与物体或 NPC 交互。
        *   `UseTool(tool, x, y)`: 切换工具并在指定格点使用。
        *   `ItemAction(item, target)`: 使用/吃掉/穿戴物品。
    *   **战术组合技能 (Tactical Combos)**：
        *   `ClearArea(rect)`: 自动清理区域内的杂草、树木、石头。
        *   `TendCrops(rect)`: 自动完成区域内的浇水和收获。
        *   `ShopSequence(npc, items)`: 自动走向商店并购买指定物品。
    *   **实时决策表 (Decision Table)**：
        *   针对“怪物围攻”等高频实时场景，由本地决策表接管。
        *   实现 `AutoCombat`: 毫秒级走位（Kiting）、挥剑和紧急补血。
    *   **路径规划**：内置 A* 算法，处理语义化指令（如 `go_to("Pierre's")`）。
    *   **状态冻结 (Pause)**：在执行战略层同步决策请求时，强制暂停游戏时间。

### 2.3 通信协议 (MCP)
*   **Server (Python)**：作为 MCP Server，暴露 `get_memory`, `update_tactics`, `generate_plan` 等工具。
*   **Client (C# Mod)**：作为 MCP Client，调用工具推送状态并获取指令。

## 3. 核心流程
1.  **系统初始化**：AI 主动询问用户长期目标，存入 Mem0。
2.  **每日循环**：
    *   **AM 6:00**：Mod 暂停游戏 -> 推送截图+状态 -> LLM 生成 `Plan` + `tactics.json` -> 恢复游戏。
    *   **执行中**：Mod 执行 `Plan`。高频战斗由 `Decision Table` 接管，无需请示 LLM。
    *   **触发器**：遇到特殊情况（如体力耗尽），Mod 暂停游戏 -> 请求 LLM 实时干预。
    *   **PM 10:00+**：Mod 推送全天总结 -> LLM 复盘并更新记忆。

## 4. 技术栈
*   **游戏端**：C#, SMAPI (Stardew Modding API)。
*   **AI 端**：Python 3.10+, LangChain/AutoGen, Mem0, ChromaDB。
*   **协议**：MCP (Model Context Protocol) via JSON-RPC。
*   **视觉**：LLM 原生多模态能力 (Vision API)。
