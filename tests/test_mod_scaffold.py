import os
import json

def test_manifest_exists():
    print("Checking if environment/mod_template/manifest.json exists...")
    assert os.path.exists("environment/mod_template/manifest.json"), "manifest.json does not exist"

def test_manifest_content():
    print("Checking content of environment/mod_template/manifest.json...")
    with open("environment/mod_template/manifest.json", "r") as f:
        content = json.load(f)
    
    expected_fields = {
        "Name": "Stardew Valley AI Agent",
        "Author": "StardewAI Team",
        "Version": "1.0.0",
        "Description": "An AI-powered automation system for Stardew Valley.",
        "UniqueID": "StardewAI.Agent",
        "EntryDll": "StardewAIAgent.dll",
        "MinimumApiVersion": "4.0.0"
    }
    
    for key, val in expected_fields.items():
        assert content.get(key) == val, f"Manifest field '{key}' mismatch: expected '{val}', got '{content.get(key)}'"

def test_modentry_exists():
    print("Checking if environment/mod_template/ModEntry.cs exists...")
    assert os.path.exists("environment/mod_template/ModEntry.cs"), "ModEntry.cs does not exist"

def test_modentry_content():
    print("Checking content of environment/mod_template/ModEntry.cs...")
    with open("environment/mod_template/ModEntry.cs", "r") as f:
        content = f.read()
    
    required_strings = [
        "using StardewModdingAPI;",
        "namespace StardewAIAgent",
        "public class ModEntry : Mod",
        "public override void Entry(IModHelper helper)",
        "Stardew AI Agent initialized."
    ]
    
    for rs in required_strings:
        assert rs in content, f"ModEntry.cs missing expected content: {rs}"

if __name__ == "__main__":
    try:
        test_manifest_exists()
        test_manifest_content()
        test_modentry_exists()
        test_modentry_content()
        print("All scaffold tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
