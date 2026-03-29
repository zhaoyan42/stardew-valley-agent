# Environment Preparation and Basic Scaffolding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Initialize the project environment with Python requirements and a basic SMAPI mod template.

**Architecture:** 
- `environment/requirements.txt`: Python dependency management.
- `environment/mod_template/`: A starting point for SMAPI mods containing a manifest and entry class.
- `tests/`: TDD-focused verification scripts.

**Tech Stack:** Python, C#, SMAPI (Stardew Modding API), TDD.

---

### Task 1: Python requirements.txt

**Files:**
- Create: `environment/requirements.txt`
- Test: `tests/test_requirements.py`

- [ ] **Step 1: Write the failing test**

```python
import os

def test_requirements_exists():
    assert os.path.exists("environment/requirements.txt")

def test_requirements_content():
    required = ["mcp", "langchain", "mem0ai", "chromadb", "openai", "anthropic", "python-dotenv"]
    with open("environment/requirements.txt", "r") as f:
        content = f.read()
    for pkg in required:
        assert pkg in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_requirements.py`
Expected: FAIL (FileNotFoundError)

- [ ] **Step 3: Create environment/requirements.txt**

```text
mcp
langchain
mem0ai
chromadb
openai
anthropic
python-dotenv
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_requirements.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add environment/requirements.txt tests/test_requirements.py
git commit -m "feat: add python requirements"
```

---

### Task 2: SMAPI Mod manifest.json

**Files:**
- Create: `environment/mod_template/manifest.json`
- Test: `tests/test_manifest.py`

- [ ] **Step 1: Write the failing test**

```python
import os
import json

def test_manifest_exists():
    assert os.path.exists("environment/mod_template/manifest.json")

def test_manifest_structure():
    with open("environment/mod_template/manifest.json", "r") as f:
        data = json.load(f)
    
    required_keys = ["Name", "Author", "Version", "Description", "UniqueID", "EntryDll"]
    for key in required_keys:
        assert key in data
    
    assert data["UniqueID"].startswith("StardewAI.")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_manifest.py`
Expected: FAIL (FileNotFoundError)

- [ ] **Step 3: Create environment/mod_template/manifest.json**

```json
{
  "Name": "Stardew Valley AI Agent",
  "Author": "StardewAI Team",
  "Version": "1.0.0",
  "Description": "An AI-powered automation system for Stardew Valley.",
  "UniqueID": "StardewAI.Agent",
  "EntryDll": "StardewAIAgent.dll",
  "MinimumApiVersion": "4.0.0",
  "UpdateKeys": []
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_manifest.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add environment/mod_template/manifest.json tests/test_manifest.py
git commit -m "feat: add SMAPI mod manifest template"
```

---

### Task 3: SMAPI Mod ModEntry.cs

**Files:**
- Create: `environment/mod_template/ModEntry.cs`
- Test: `tests/test_mod_entry.py`

- [ ] **Step 1: Write the failing test**

```python
import os

def test_mod_entry_exists():
    assert os.path.exists("environment/mod_template/ModEntry.cs")

def test_mod_entry_content():
    with open("environment/mod_template/ModEntry.cs", "r") as f:
        content = f.read()
    
    assert "using StardewModdingAPI;" in content
    assert "public class ModEntry : Mod" in content
    assert "public override void Entry(IModHelper helper)" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_mod_entry.py`
Expected: FAIL (FileNotFoundError)

- [ ] **Step 3: Create environment/mod_template/ModEntry.cs**

```csharp
using System;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;

namespace StardewAIAgent
{
    /// <summary>The mod entry point.</summary>
    public class ModEntry : Mod
    {
        /*********
        ** Public methods
        *********/
        /// <summary>The mod entry point, called after the mod is first loaded.</summary>
        /// <param name="helper">Provides simplified APIs for writing mods.</param>
        public override void Entry(IModHelper helper)
        {
            this.Monitor.Log("Stardew AI Agent initialized.", LogLevel.Debug);
        }
    }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_mod_entry.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add environment/mod_template/ModEntry.cs tests/test_mod_entry.py
git commit -m "feat: add SMAPI ModEntry template"
```
