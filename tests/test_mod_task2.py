import os
import json

def test_new_files_exist():
    print("Checking if new files exist...")
    assert os.path.exists("environment/mod_template/Communication/McpClient.cs"), "McpClient.cs does not exist"
    assert os.path.exists("environment/mod_template/Models/PlayerStatus.cs"), "PlayerStatus.cs does not exist"

def test_modentry_new_methods():
    print("Checking for new methods in ModEntry.cs...")
    with open("environment/mod_template/ModEntry.cs", "r", encoding='utf-8') as f:
        content = f.read()
    
    required_methods = [
        "TakeScreenshot",
        "ExportStatus",
        "RequestDecision",
        "ai_screenshot",
        "ai_export_status",
        "ai_request_decision"
    ]
    
    for method in required_methods:
        assert method in content, f"ModEntry.cs missing expected method or command: {method}"

def test_mcpclient_content():
    print("Checking content of McpClient.cs...")
    with open("environment/mod_template/Communication/McpClient.cs", "r", encoding='utf-8') as f:
        content = f.read()
    
    required_strings = [
        "public async Task<string> SendStateAsync",
        "public async Task<string> GetDecisionAsync",
        "JsonConvert.SerializeObject(state)"
    ]
    
    for rs in required_strings:
        assert rs in content, f"McpClient.cs missing expected content: {rs}"

def test_playerstatus_content():
    print("Checking content of PlayerStatus.cs...")
    with open("environment/mod_template/Models/PlayerStatus.cs", "r", encoding='utf-8') as f:
        content = f.read()
    
    required_fields = [
        "public int Money",
        "public float Stamina",
        "public int Health",
        "public string Location",
        "public static PlayerStatus Capture()"
    ]
    
    for field in required_fields:
        assert field in content, f"PlayerStatus.cs missing expected field: {field}"

if __name__ == "__main__":
    try:
        test_new_files_exist()
        test_modentry_new_methods()
        test_mcpclient_content()
        test_playerstatus_content()
        print("All Task 2 tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
