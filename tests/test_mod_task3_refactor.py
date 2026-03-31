import os

def test_new_actionqueue_exists():
    print("Checking if ActionQueue.cs exists...")
    assert os.path.exists("environment/mod_template/StardewValleyAI/Actions/ActionQueue.cs"), "ActionQueue.cs does not exist"

def test_atomicactions_robustness():
    print("Checking robustness improvements in AtomicActions.cs...")
    with open("environment/mod_template/StardewValleyAI/Actions/AtomicActions.cs", "r", encoding='utf-8') as f:
        content = f.read()
    
    required_strings = [
        "Game1.player.stamina <= 0",
        "tileX * 64 + 32",
        "tileY * 64 + 32",
        "actionObj.placementAction",
        "Utility.withinRadiusOfPlayer"
    ]
    
    for rs in required_strings:
        assert rs in content, f"AtomicActions.cs missing expected content: {rs}"

def test_tacticalcombos_tick_based():
    print("Checking tick-based queue in TacticalCombos.cs...")
    with open("environment/mod_template/StardewValleyAI/Actions/TacticalCombos.cs", "r", encoding='utf-8') as f:
        content = f.read()
    
    required_strings = [
        "ActionQueue.Enqueue",
        "new ToolAction",
        "new InteractAction",
        "class ShopAction : IAction",
        "shopMenu.receiveLeftClick"
    ]
    
    for rs in required_strings:
        assert rs in content, f"TacticalCombos.cs missing expected content: {rs}"

def test_modentry_integration():
    print("Checking integration in ModEntry.cs...")
    with open("environment/mod_template/ModEntry.cs", "r", encoding='utf-8') as f:
        content = f.read()
    
    required_strings = [
        "ActionQueue.Initialize",
        "OnUpdateTicked",
        "ActionQueue.Update()"
    ]
    
    for rs in required_strings:
        assert rs in content, f"ModEntry.cs missing expected content: {rs}"

if __name__ == "__main__":
    try:
        test_new_actionqueue_exists()
        test_atomicactions_robustness()
        test_tacticalcombos_tick_based()
        test_modentry_integration()
        print("All Task 3 Refactor tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
