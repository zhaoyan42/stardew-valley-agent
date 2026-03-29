# 星露谷物语 AI 自动化系统实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个基于战略-战术双层架构的星露谷物语全自动 AI 决策与控制系统。

**Architecture:** 采用 Python (战略层) + C# SMAPI (战术层) 架构。战略层负责 LLM 决策、视觉感知和混合记忆（OpenViking + Mem0）；战术层负责 SMAPI Mod 实时执行、A* 寻路、原子动作库和本地决策表。两者通过 MCP 协议通信。

**Tech Stack:** C#, SMAPI, Python 3.10+, LangChain, Mem0, ChromaDB, MCP SDK.

---

### 任务 1: 环境准备与基础脚手架
*   创建 Python `requirements.txt`。
*   初始化 SMAPI Mod 基础结构 (manifest.json, ModEntry.cs)。

### 任务 2: 战术层 (C#) - 感知、暂停与基础通信
*   实现游戏截图与状态导出 (JSON)。
*   实现同步决策时的游戏暂停逻辑 (Game1.activeClickableMenu)。
*   搭建 MCP Client 基础，准备连接 Python Server。

### 任务 3: 战术层 (C#) - 原子动作库与组合技能
**Files:**
- Create: `StardewValleyAI/Actions/AtomicActions.cs`
- Create: `StardewValleyAI/Actions/TacticalCombos.cs`

- [ ] **步骤 1: 实现原子动作库 (Interact, UseTool, ItemAction)**
- [ ] **步骤 2: 实现区域清理组合技能 (ClearArea)**
- [ ] **步骤 3: 实现作物护理组合技能 (TendCrops)**
- [ ] **步骤 4: 实现购物序列组合技能 (ShopSequence)**

### 任务 4: 战术层 (C#) - A* 寻路与实时决策表
- [ ] **步骤 1: 实现 A* 寻路逻辑 (自动避障)**
- [ ] **步骤 2: 实现实时决策表 (AutoCombat)，支持毫秒级走位与补血**

### 任务 5: 战略层 (Python) - 混合记忆系统
- [ ] **步骤 1: 集成 Mem0 + ChromaDB (动态经验)**
- [ ] **步骤 2: 实现 OpenViking 风格层级 Wiki 加载器 (静态知识库)**

### 任务 6: 战略层 (Python) - MCP Server 与 LLM 编排
- [ ] **步骤 1: 编写 MCP Server，暴露 `execute_combo`, `get_plan` 等工具**
- [ ] **步骤 2: 编写 LLM 提示词模板 (整合视觉、数据与战术建议)**
- [ ] **步骤 3: 实现每日复盘与 `tactics.json` 参数优化逻辑**

### 任务 7: 联调与初始化向导
- [ ] **步骤 1: 实现开局“面试”引导**
- [ ] **步骤 2: 完整链路测试与战术演进验证**
